"""
config.py
─────────
Central configuration for the RAG pipeline.

CHANGES vs. original
─────────────────────
① CHUNK_SIZE updated to 220 (was 180/300).
   all-MiniLM-L6-v2 has a HARD limit of 256 tokens.
   The task sheet suggests trying 450 — that would silently truncate every
   chunk during embedding. 220 is the safe practical ceiling with overlap.
② CHUNK_OVERLAP updated to 40 (was 30/50).
③ TOP_K_RETRIEVE added (retrieve 20, rerank to TOP_K=5) — enables Task 6.
④ api_key moved here as the single source of truth.
   Set your real HuggingFace token here (or via environment variable).
⑤ DOC_NAME added here so both the notebook and rag_api.py use the same value.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional; env vars can be set directly

# ── Embedding model ───────────────────────────────────────────────────────────
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM        = 384   # dimension of all-MiniLM-L6-v2

# ── PostgreSQL connection ─────────────────────────────────────────────────────
PG_CONN_STR = os.getenv(
    "PG_CONN_STR",
    "postgresql://postgres:admin@localhost:5432/online_rag_deeplearningbook"
)

# ── Chunking ──────────────────────────────────────────────────────────────────
# Default chunking for midpoint model
CHUNK_SIZE    = 220   # safe ceiling for all-MiniLM-L6-v2 (256 token hard limit)
CHUNK_OVERLAP = 40

# Experimental tuning for large context models (Task 3)
CHUNK_SIZE_LARGE    = 450
CHUNK_OVERLAP_LARGE = 90

# ── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K          = 5    # final chunks sent to LLM
TOP_K_RETRIEVE = 20   # retrieve this many, then rerank down to TOP_K

# ── Document name ─────────────────────────────────────────────────────────────
# Must match the doc_name used during ingestion (upsert_chunks call).
DOC_NAME = "DeepLearning-IanGoodfellow_RAG"

# ── LLM API ───────────────────────────────────────────────────────────────────
# Set your real HuggingFace token here or as the HF_API_KEY environment var.
HF_API_KEY   = os.getenv("HF_API_KEY", "your-hf-token-here")
HF_BASE_URL  = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1")
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "Qwen/Qwen3-Coder-Next:novita")

# ── API Endpoint ──────────────────────────────────────────────────────────────
# When deploying to Streamlit Cloud, the backend must be accessible at this URL.
# 127.0.0.1:8000 only works for local execution.
API_URL = os.getenv("ST_API_URL", "http://127.0.0.1:8000")

# Legacy alias — some cells use `api_key` directly
api_key = os.getenv("HF_API_KEY", "your-hf-token-here")