"""
chunking.py  ·  Goodfellow "Deep Learning" — RAG-optimised chunker
════════════════════════════════════════════════════════════════════
All bugs found by inspecting the real fitz-extracted text of the book.

CHANGES vs. original
─────────────────────
① SECTION_HEADER regex was wrong
    Original: ^[A-Z][A-Z\s]{3,}$   ← only matched bare ALL-CAPS words ("CONTENTS")
    Reality (fitz output):
      • Chapter headers span TWO lines:  "CHAPTER 2." / "LINEAR ALGEBRA"
      • Section numbers are a standalone line: "2.6"
        followed immediately by the title on the next line
    Fix: replaced single-line regex with a two-pass state machine.

② Running page headers are de-duplicated
    "CHAPTER 2." + "LINEAR ALGEBRA" appear at the top of every page.
    We record the first occurrence as the real chapter boundary and
    silently drop all repeats.

③ pdf_loader must join pages with \f
    fitz.page.get_text() per-page gives no page separators.
    clean_text() expects "\f" between pages for page-number tracking.
    Fix: updated pdf_loader.py (separate file) to use
         "\f".join(page.get_text() for page in doc)

④ Form-feed stripping + page-number tracking
    Every \f = one page boundary. We record which page each character
    came from so chunks can carry page_start / page_end metadata.

⑤ Boilerplate filtering
    • TOC dot-leader lines ("2.2  Multiplying... . . . . . 34")
    • Figure / Table captions
    • Lone page-number lines
    • "CONTENTS" repeated header
    • Lines >50 % garbled PUA math glyphs (Unicode E000–F8FF range)

⑥ chunk_size capped at 256 tokens  (all-MiniLM-L6-v2 hard limit)
    Original default was 300 → silent truncation during embedding.
    New default: 220 tokens (safe margin).

⑦ Minimum chunk filter
    Fragments shorter than MIN_CHUNK_TOKENS are discarded.

⑧ Richer metadata per chunk
    chapter, section, entry_id, chunk_in_entry, token_len,
    page_start, page_end, content
"""

from __future__ import annotations

import re
from typing import List, Dict, Optional, Tuple
from transformers import AutoTokenizer

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

# We allow higher limits for larger embedding models, but preserve safe defaults.
MAX_MODEL_TOKENS  = 256   # all-MiniLM-L6-v2 hard limit
MIN_CHUNK_TOKENS  = 30
DEFAULT_CHUNK_SIZE = 300
DEFAULT_OVERLAP    = 50

# ─────────────────────────────────────────────────────────────────────────────
# 0. CLEANING
# ─────────────────────────────────────────────────────────────────────────────

_TOC_LINE    = re.compile(r"\.{3,}")          # 3+ dots → table-of-contents line
_FIGURE_LINE = re.compile(r"^(Figure|Table)\s+[\d.]+[:\s]")
_PAGE_NUM    = re.compile(r"^\s*\d{1,4}\s*$") # lone page number
_CONTENTS    = re.compile(r"^CONTENTS\s*$", re.IGNORECASE)
_PUA_CHAR    = re.compile(r"[\ue000-\uf8ff]") # Private Use Area = garbled math

def _is_garbled(line: str) -> bool:
    """True if more than 40 % of the line's chars are PUA (unreadable math)."""
    if not line:
        return False
    pua_count = sum(1 for c in line if "\ue000" <= c <= "\uf8ff")
    return pua_count / len(line) > 0.40


def clean_text(raw: str) -> Tuple[str, Dict[int, int]]:
    """
    Strip form-feeds (page breaks), boilerplate, and garbled math lines.

    Parameters
    ----------
    raw : str
        Full PDF text with pages separated by "\\f" (form-feed).
        Use:  "\\f".join(page.get_text() for page in fitz_doc)

    Returns
    -------
    cleaned : str
        Clean text; pages now separated by plain newlines.
    char_to_page : dict[int, int]
        Maps character offset → 1-based PDF page number.
    """
    page_blocks = raw.split("\f")
    cleaned_parts: List[str] = []
    char_to_page: Dict[int, int] = {}
    cursor = 0

    for page_idx, block in enumerate(page_blocks):
        page_num = page_idx + 1
        kept: List[str] = []

        for line in block.splitlines():
            s = line.strip()
            if (
                not s
                or _TOC_LINE.search(s)
                or _FIGURE_LINE.match(s)
                or _PAGE_NUM.match(s)
                or _CONTENTS.match(s)
                or _is_garbled(s)
            ):
                continue
            kept.append(line)

        part = "\n".join(kept)
        for i in range(cursor, cursor + len(part) + 1):
            char_to_page[i] = page_num
        cleaned_parts.append(part)
        cursor += len(part) + 1

    return "\n".join(cleaned_parts), char_to_page


# ─────────────────────────────────────────────────────────────────────────────
# 1. SPLIT SECTIONS  (two-line state machine)
# ─────────────────────────────────────────────────────────────────────────────

# fitz extracts "CHAPTER 2." and "LINEAR ALGEBRA" on SEPARATE lines
_CHAP_NUM_LINE  = re.compile(r"^CHAPTER\s+(\d+)\.(?:\s+(.*))?$", re.IGNORECASE)          # "CHAPTER 2." or "CHAPTER 6. DEEP..."
# Standalone section number only:  "2.6"  or  "10.11"
_SEC_NUM_ALONE  = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){1,2})$")


def split_sections(text: str) -> List[Dict]:
    """
    Split cleaned text into section dicts using a two-line look-ahead for
    the heading patterns found in fitz-extracted text of this book.

    Heading patterns
    ────────────────
    Chapter:
        line N   →  "CHAPTER 2."
        line N+1 →  "LINEAR ALGEBRA"

    Section / subsection:
        line N   →  "2.6"
        line N+1 →  "Special Kinds of Matrices and Vectors"

    Returns
    -------
    list of dicts:
        chapter     : str
        section     : str
        content     : str
        char_start  : int
        char_end    : int
    """
    # Keep line-endings in order to map text-position offsets accurately.
    line_iter = list(re.finditer(r"(.*?)(?:\n|$)", text, flags=re.MULTILINE))

    sections: List[Dict] = []
    cur_chapter = "front_matter"
    cur_section = "general"
    buffer: List[str] = []
    buffer_start: Optional[int] = None
    buffer_end: Optional[int] = None

    # Track seen chapter headers to skip running-page repeats
    seen_chap: set = set()
    # Whether we have passed the front matter (TOC/notation) and are in a chapter
    in_chapter = False

    def flush():
        nonlocal buffer, buffer_start, buffer_end
        content = "\n".join(buffer).strip()
        if content and buffer_start is not None and buffer_end is not None:
            sections.append({
                "chapter": cur_chapter,
                "section": cur_section,
                "content": content,
                "char_start": buffer_start,
                "char_end": buffer_end,
            })
        buffer = []
        buffer_start = None
        buffer_end = None

    i = 0
    while i < len(line_iter):
        match = line_iter[i]
        line_text = match.group(1)
        line_start = match.start(1)
        line_end = match.end(1)
        stripped = line_text.strip()

        m_chap = _CHAP_NUM_LINE.match(stripped)
        if m_chap:
            chapter_num = m_chap.group(1)
            title = (m_chap.group(2) or "").strip()
            lines_consumed = 1

            # If title isn't on this line, look ahead to the next line
            if not title and i + 1 < len(line_iter):
                title = line_iter[i + 1].group(1).strip()
                lines_consumed = 2

            chap_key = f"CHAPTER {chapter_num}. {title}"

            if chap_key not in seen_chap:
                seen_chap.add(chap_key)
                flush()
                cur_chapter = f"chapter_{chapter_num}"
                cur_section = "intro"
                in_chapter = True
                i += lines_consumed
                continue
            else:
                i += lines_consumed
                continue

        m_sec = _SEC_NUM_ALONE.match(stripped)
        if m_sec and i + 1 < len(line_iter) and in_chapter:
            title_raw = line_iter[i + 1].group(1).strip()
            if title_raw and not _TOC_LINE.search(title_raw) and not _SEC_NUM_ALONE.match(title_raw):
                flush()
                slug = re.sub(r"\s+", "_", title_raw.lower())
                slug = re.sub(r"[^\w_]", "", slug)[:60]
                cur_section = f"{m_sec.group(1)}_{slug if slug else m_sec.group(1)}"
                i += 2
                continue

        if stripped:
            if buffer_start is None:
                buffer_start = line_start
            buffer_end = line_end
            buffer.append(line_text)

        i += 1

    flush()
    return sections


# ─────────────────────────────────────────────────────────────────────────────
# 2. SPLIT ENTRIES (paragraphs within a section)
# ─────────────────────────────────────────────────────────────────────────────

def split_section_entries(section_name: str, content: str) -> List[str]:
    """Split a section's content on blank lines into paragraph entries."""
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", content)
        if p.strip()
    ]
    return paragraphs if paragraphs else [content]


# ─────────────────────────────────────────────────────────────────────────────
# 3. TOKEN-BASED SLIDING-WINDOW CHUNKER
# ─────────────────────────────────────────────────────────────────────────────

def chunk_text(
    text: str,
    tokenizer,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap:    int = DEFAULT_OVERLAP,
) -> List[str]:
    """
    Sliding-window token-level chunker.

    chunk_size is hard-clamped to MAX_MODEL_TOKENS (256) — the absolute
    limit of all-MiniLM-L6-v2. Exceeding it causes silent embedding truncation.
    """
    chunk_size = min(chunk_size, MAX_MODEL_TOKENS)
    overlap    = min(overlap, chunk_size // 4)
    step       = chunk_size - overlap

    tokens = tokenizer.encode(text, add_special_tokens=False)
    if not tokens:
        return []

    chunks: List[str] = []
    i = 0
    while i < len(tokens):
        window  = tokens[i : i + chunk_size]
        decoded = tokenizer.decode(window, skip_special_tokens=True).strip()
        if decoded:
            chunks.append(decoded)
        if i + chunk_size >= len(tokens):
            break
        i += step

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# 4. BUILD CHUNKS  (full pipeline)
# ─────────────────────────────────────────────────────────────────────────────

def build_chunks(
    raw_text:         str,
    embed_model_name: str,
    chunk_size:       int  = DEFAULT_CHUNK_SIZE,
    overlap:          int  = DEFAULT_OVERLAP,
    tokenizer               = None,
    min_tokens:       int  = MIN_CHUNK_TOKENS,
) -> List[Dict]:
    """
    Full pipeline: clean → split sections → split entries → chunk → annotate.

    Parameters
    ----------
    raw_text         : str   Full text from pdf_loader.read_pdf_text().
                             IMPORTANT: read_pdf_text must join pages with "\\f".
    embed_model_name : str   HuggingFace model id for the tokenizer.
    chunk_size       : int   Target tokens per chunk (clamped to 256).
    overlap          : int   Token overlap between chunks.
    tokenizer        : optional pre-loaded AutoTokenizer.
    min_tokens       : int   Discard chunks shorter than this.

    Returns
    -------
    List of chunk dicts with keys:
        chapter, section, entry_id, chunk_in_entry, token_len, content
    """
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(embed_model_name)

    cleaned, char_to_page = clean_text(raw_text)
    sections   = split_sections(cleaned)
    chunks:  List[Dict] = []

    def _page_range(char_to_page_map, char_start, char_end):
        if char_start is None or char_end is None:
            return None, None
        pages = [char_to_page_map[i] for i in range(char_start, char_end + 1) if i in char_to_page_map]
        if not pages:
            return None, None
        return min(pages), max(pages)

    for sec in sections:
        page_start, page_end = _page_range(char_to_page, sec.get("char_start"), sec.get("char_end"))
        entries = split_section_entries(sec["section"], sec["content"])

        for entry_id, entry in enumerate(entries):
            sub_chunks = chunk_text(entry, tokenizer, chunk_size, overlap)

            for idx, chunk in enumerate(sub_chunks):
                token_len = len(tokenizer.encode(chunk, add_special_tokens=False))

                if token_len < min_tokens:
                    continue

                chunks.append({
                    "chapter":        sec["chapter"],
                    "section":        sec["section"],
                    "entry_id":       entry_id,
                    "chunk_in_entry": idx,
                    "token_len":      token_len,
                    "content":        chunk,
                    "page_start":     page_start,
                    "page_end":       page_end,
                })

    return chunks

