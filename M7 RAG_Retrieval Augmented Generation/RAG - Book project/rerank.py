"""
rerank.py
─────────
Post-retrieval re-ranking.

Takes the raw DB rows (section, content, cosine_sim) returned by
retrieve_topk and adds a final_score by combining:

  1. Vector similarity  (cosine_sim from pgvector)     weight = 0.7
  2. Keyword overlap    (question terms ∩ chunk text)  weight = 0.3

Returns a list of 4-tuples so the notebook HTML loop can unpack:
    section, content, cosine_sim, final_score = row

BUG FIXED: original returned the string "scored_results" — nothing worked.
"""

import re
from typing import List, Tuple


def _keyword_score(question: str, content: str) -> float:
    """
    Fraction of question tokens (≥ 3 chars) that appear in the chunk text.
    Returns a float in [0, 1].
    """
    q_tokens = set(re.findall(r"\b\w{3,}\b", question.lower()))
    if not q_tokens:
        return 0.0
    c_lower = content.lower()
    hits = sum(1 for t in q_tokens if t in c_lower)
    return hits / len(q_tokens)


def rerank_results(
    question: str,
    results: List[Tuple],
    vec_weight: float = 0.7,
    kw_weight:  float = 0.3,
) -> List[Tuple]:
    """
    Re-rank retrieved chunks by a combined vector + keyword score.

    Parameters
    ----------
    question   : str         The user's question string.
    results    : list of 5-tuples  (chapter, section, chunk_index, content, cosine_sim)
                 as returned by retrieve_topk / SEARCH_CHUNKS_SQL.
    vec_weight : float       Weight applied to cosine similarity (default 0.7).
    kw_weight  : float       Weight applied to keyword overlap   (default 0.3).

    Returns
    -------
    List of 4-tuples: (section, content, cosine_sim, final_score)
    Sorted by final_score descending.
    """
    scored = []
    for row in results:
        # SEARCH_CHUNKS_SQL returns: (chapter, section, chunk_index, content, cosine_sim)
        section    = row[1] if len(row) > 1 else ""
        content    = row[3] if len(row) > 3 else ""
        cosine_sim = float(row[4]) if len(row) > 4 and row[4] is not None else 0.0

        kw_score   = _keyword_score(question, content)
        final      = vec_weight * cosine_sim + kw_weight * kw_score

        scored.append((section, content, cosine_sim, final))

    return sorted(scored, key=lambda x: x[3], reverse=True)


def cross_encoder_rerank(
    query: str,
    candidates: list,
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2",
    top_k: int = 5,
) -> list:
    """Re-rank candidate chunks with a cross-encoder.

    candidates: list of dicts with keys section, content, maybe chapter.
    """
    try:
        from sentence_transformers import CrossEncoder
    except Exception as e:
        raise RuntimeError("Install sentence-transformers to enable cross-encoder reranking") from e

    xencoder = CrossEncoder(model_name)
    pairs = [(query, c.get("content", "")) for c in candidates]
    scores = xencoder.predict(pairs)

    ranked = sorted(
        zip(candidates, scores), key=lambda x: x[1], reverse=True
    )[:top_k]

    return [dict(**c, cross_score=float(score)) for c, score in ranked]
