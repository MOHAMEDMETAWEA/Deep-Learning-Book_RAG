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
from retrieval import retrieve_topk
from rerank import rerank_results
from pdf_loader import read_pdf_text2, read_bdf_text
from chunking import build_chunks
from db import init_db, upsert_chunks


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")


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
    """Convert a 4-tuple from rerank_results into a clean dict."""
    section    = row[0] if len(row) > 0 else ""
    content    = row[1] if len(row) > 1 else ""
    cosine_sim = float(row[2]) if len(row) > 2 and row[2] is not None else 0.0
    final_score = float(row[3]) if len(row) > 3 and row[3] is not None else cosine_sim
    return {
        "section":          section or "",
        "content":          content or "",
        "vector_similarity": cosine_sim,
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

app = FastAPI(title="Deep Learning RAG API", version="2.0.0")
embedder = load_embedder(EMBED_MODEL_NAME)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "doc": DOC_NAME}


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
        # 1. Embed question
        qvec = embedder.encode(
            [question], normalize_embeddings=True
        )[0].astype(np.float32)

        # 2. Retrieve broader candidate set
        raw_results = retrieve_topk(PG_CONN_STR, DOC_NAME, qvec, TOP_K_RETRIEVE)

        # 3. Rerank → now returns 4-tuples (section, content, cosine_sim, final_score)
        reranked = rerank_results(question, raw_results)

        # 4. Take top TOP_K for LLM context
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
