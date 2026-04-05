"""
rag_api.py
──────────
FastAPI service exposing the RAG pipeline over HTTP.

CHANGES vs. original
─────────────────────
① DOC_NAME was hardcoded as "BaraaCV" — retrieving from the wrong document,
   returning 0 results for every question. Fixed to use config.DOC_NAME.
② api_key was a literal " " (space). Now read from config.HF_API_KEY which
   reads the HF_API_KEY environment variable.
③ _build_client() now checks for a genuinely empty key and raises a clear
   500 error instead of silently sending a space as the bearer token.
④ /ask now retrieves TOP_K_RETRIEVE chunks, reranks, then sends TOP_K to LLM.
⑤ rerank_results is now actually called (it was imported but never used).
⑥ Type annotations updated for Python 3.9+ compatibility (no X | Y union).
"""


from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field
from config import (
    EMBED_MODEL_NAME,
    EMBED_DIM,
    PG_CONN_STR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    TOP_K_RETRIEVE,
    DOC_NAME,
    HF_API_KEY,
    HF_BASE_URL,
    HF_MODEL_NAME,
)
from embeddings import load_embedder, embed_chunks
from retrieval import hybrid_retrieve_topk
from rerank import rerank_results
from pdf_loader import read_pdf_text2, read_bdf_text
from chunking import build_chunks
from db import init_db, upsert_chunks
from query_expansion import expand_query


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    filter_chapters: Optional[list] = None


# ─────────────────────────────────────────────────────────────────────────────
# LLM helpers
# ─────────────────────────────────────────────────────────────────────────────

def generate_text(client: OpenAI, context: str, question: str) -> str:
    prompt = f"""
You are an AI assistant that answers questions strictly using the provided CONTEXT.

STRICT RULES:
- Use ONLY the information inside the CONTEXT.
- Do NOT use prior knowledge or external information.
- If the answer is not clearly present in the CONTEXT, respond exactly with:
  "The answer is not found in the provided context."
- Prefer quoting or closely paraphrasing the CONTEXT.

Answer style:
- Keep the answer clear and concise.
- Use bullet points when listing multiple facts.

Output format:

Answer:
<answer based strictly on the context>

Source:
<section name if available>

--------------------------------

CONTEXT:
{context}

QUESTION:
{question}
"""
    completion = client.chat.completions.create(
        model=HF_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1024,
    )
    return completion.choices[0].message.content.strip()


def _normalize_row(row: tuple) -> dict:
    """Convert a 6-tuple from rerank_results into a clean dict."""
    chapter    = row[0] if len(row) > 0 else ""
    section    = row[1] if len(row) > 1 else ""
    chunk_idx  = row[2] if len(row) > 2 else 0
    content    = row[3] if len(row) > 3 else ""
    base_score = float(row[4]) if len(row) > 4 and row[4] is not None else 0.0
    final_score = float(row[5]) if len(row) > 5 and row[5] is not None else base_score
    return {
        "chapter":           chapter or "",
        "section":           section or "",
        "chunk_index":       chunk_idx,
        "content":           content or "",
        "base_similarity":   base_score,
        "final_score":       final_score,
    }


def _build_client() -> Optional[OpenAI]:
    key = HF_API_KEY.strip()
    if not key or key == "your-hf-token-here":
        return None
    return OpenAI(base_url=HF_BASE_URL, api_key=key)


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Deep Learning RAG API", version="2.2.1-FIXED")

# 1. CORS for Streamlit / Frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedder = load_embedder(EMBED_MODEL_NAME)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "doc": DOC_NAME}


@app.get("/chapters")
def get_chapters() -> dict:
    from db import get_all_chapters
    try:
        chapters = get_all_chapters(PG_CONN_STR, DOC_NAME)
        return {"chapters": chapters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask_question(payload: AskRequest) -> dict:
    client = _build_client()
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="HF API key missing or invalid. Set HF_API_KEY environment variable.",
        )

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # 1. Query Expansion (Task 7)
        expanded = expand_query(question)
        search_query = expanded["expanded"]  # or rewrite

        # 2. Embed question
        qvec = embedder.encode(
            [search_query], normalize_embeddings=True
        )[0].astype(np.float32)

        # 3. Hybrid Retrieval (Task 5) + Filtering
        raw_results = hybrid_retrieve_topk(
            PG_CONN_STR, DOC_NAME, qvec, search_query, TOP_K_RETRIEVE,
            filter_chapters=payload.filter_chapters
        )

        # 4. Rerank (Task 6)
        reranked = rerank_results(question, raw_results)

        # 5. Take top TOP_K for LLM context
        top_chunks = [_normalize_row(r) for r in reranked[:TOP_K]]

        if top_chunks:
            context = "\n\n".join(
                f"SECTION: {c['section']}\n{c['content']}"
                for c in top_chunks
            )
            generated_answer = generate_text(client, context, question)
        else:
            generated_answer = "The answer is not found in the provided context."

        return {
            "Generated Answer":       generated_answer,
            "Top Retrieved Chunks":   top_chunks,
            "Query Expansion":         expanded,
        }

    except HTTPException:
        raise
    except Exception as exc:
        msg = str(exc)
        if "401" in msg or "Invalid username or password" in msg:
            raise HTTPException(
                status_code=401,
                detail="HuggingFace authentication failed. Check your HF_API_KEY.",
            ) from exc
        raise HTTPException(
            status_code=500, detail=f"RAG pipeline failed: {exc}"
        ) from exc


class IngestRequest(BaseModel):
    source_path: str
    source_type: Optional[str] = "pdf"  # pdf|bdf|text
    chunk_size: Optional[int] = None
    overlap: Optional[int] = None
    embedding_model: Optional[str] = None


@app.post("/ingest")
def ingest_document(payload: IngestRequest) -> dict:
    source_path = payload.source_path
    source_type = (payload.source_type or "pdf").lower()

    if source_type == "pdf":
        document_text = read_pdf_text2(source_path)
    else:
        document_text = read_bdf_text(source_path)

    effective_chunk_size = payload.chunk_size or CHUNK_SIZE
    effective_overlap = payload.overlap or CHUNK_OVERLAP
    model_name = payload.embedding_model or EMBED_MODEL_NAME

    # Build chunks from raw text
    chunks = build_chunks(
        document_text,
        model_name,
        chunk_size=effective_chunk_size,
        overlap=effective_overlap,
    )

    # Embedding and database operations
    init_db(PG_CONN_STR, EMBED_DIM)
    vectors = embed_chunks(chunks, embedder)
    upsert_chunks(PG_CONN_STR, DOC_NAME, chunks, vectors)

    return {
        "status": "ingested",
        "doc_name": DOC_NAME,
        "num_chunks": len(chunks),
        "chunk_size": effective_chunk_size,
        "overlap": effective_overlap,
    }
