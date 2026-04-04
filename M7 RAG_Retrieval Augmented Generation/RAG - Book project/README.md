# RAG Pipeline for Deep Learning Book 📚

A complete **Retrieval-Augmented Generation (RAG)** system that extracts knowledge from the Deep Learning book by Ian Goodfellow, uses embeddings and vector search, and answers questions using an LLM (via HuggingFace Inference API) with source citations.

## 🎯 Project Overview

This project implements a production-ready RAG pipeline that:

- **Extracts text** from PDF documents (Deep Learning book)
- **Chunks intelligently** into overlapping segments with chapter/section metadata
- **Embeds chunks** using SentenceTransformer models (all-MiniLM-L6-v2)
- **Stores embeddings** in PostgreSQL with pgvector for vector search
- **Retrieves context** using pure vector search or hybrid (vector + keyword) search
- **Reranks results** by combining semantic similarity (70%) + keyword overlap (30%)
- **Generates answers** using LLMs (via OpenAI-compatible API / HuggingFace) with source citations
- **Exposes API** via FastAPI for easy integration

### Key Features

✅ **Smart Chunking** — Multi-pass regex state machine detects chapter/section boundaries  
✅ **Page Tracking** — Each chunk knows its source pages for citations  
✅ **Boilerplate Filtering** — Removes TOC leaders, captions, noise, math glyphs  
✅ **Hybrid Search** — Keyword + vector blended search for technical terms  
✅ **Reranking** — Two-stage retrieval → rerank → LLM for best results  
✅ **API Ready** — FastAPI server with `/ask` endpoint  
✅ **Notebook Demos** — Jupyter notebooks included for exploration  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
       ┌─────────────────────────────────────┐
       │  1. EMBEDDING QUERY                 │
       │  sentence-transformers/all-MiniLM   │
       └────────────┬────────────────────────┘
                    │
                    ▼
       ┌─────────────────────────────────────┐
       │  2. VECTOR SEARCH (retrieve 20)     │
       │  PostgreSQL + pgvector              │
       └────────────┬────────────────────────┘
                    │
                    ▼
       ┌─────────────────────────────────────┐
       │  3. RERANKING (to top 5)            │
       │  Vector similarity (0.7)             │
       │  + Keyword overlap (0.3)            │
       └────────────┬────────────────────────┘
                    │
                    ▼
       ┌─────────────────────────────────────┐
       │  4. LLM GENERATION                  │
       │  OpenAI GPT + Context               │
       │  Returns: Answer + Source           │
       └────────────┬────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI ANSWER                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### System Requirements
- **Python 3.9+**
- **PostgreSQL 13+** with pgvector extension installed
- **Git**

### External Services
- **HuggingFace API Key** — required for LLM generation (set as `HF_API_KEY`)

---

## 🚀 Installation

### Step 1: Clone Repository

```bash
cd "M7 RAG_Retrieval Augmented Generation/RAG - Book project"
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages installed:**
- `fastapi` — REST API framework
- `uvicorn` — ASGI server for FastAPI
- `sentence-transformers` — Embedding models
- `psycopg[binary]` — PostgreSQL client
- `pgvector` — Vector search support
- `openai` — OpenAI API client
- `pymupdf` — PDF text extraction
- `python-dotenv` — Environment variable loading

### Step 4: Set Up PostgreSQL with pgvector

#### Option A: Docker (Recommended)

```bash
# Pull and run PostgreSQL with pgvector
docker run --name pgvector-rag \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=online_rag_deeplearningbook \
  -p 5432:5432 \
  -d pgvector/pgvector:latest

# Verify connection
psql -h localhost -U postgres -d online_rag_deeplearningbook
```

#### Option B: Local PostgreSQL + pgvector Extension

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE online_rag_deeplearningbook;

-- Connect to the database
\c online_rag_deeplearningbook

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## ⚙️ Configuration

### Step 1: Create `.env` File

Copy the example and add your credentials:

```bash
cp .env.example .env
```

### Step 2: Edit `.env`

```env
# PostgreSQL Connection
PG_CONN_STR=postgresql://postgres:admin@localhost:5432/online_rag_deeplearningbook

# HuggingFace Configuration
HF_API_KEY=hf_...your-hf-token...
HF_BASE_URL=https://router.huggingface.co/v1
HF_MODEL_NAME=Qwen/Qwen3-Coder-Next:novita
```

### Key Configuration Parameters (`config.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model — 384 dims |
| `CHUNK_SIZE` | `220` | Max tokens per chunk (256 is hard limit) |
| `CHUNK_OVERLAP` | `40` | Tokens overlap between chunks |
| `TOP_K_RETRIEVE` | `20` | Retrieve this many before reranking |
| `TOP_K` | `5` | Final chunks sent to LLM |
| `PG_CONN_STR` | `postgresql://...` | PostgreSQL connection string |

⚠️ **Warning:** Do NOT set `CHUNK_SIZE` > 220 for all-MiniLM-L6-v2 — it silently truncates at 256.

---

## 📖 Usage

### Option 1: Jupyter Notebook (Interactive)

```bash
jupyter notebook fullsystem.ipynb
```

**Steps in notebook:**
1. **Load PDF** — Extract text from `Deep+Learning+Ian+Goodfellow.pdf`
2. **Clean & Chunk** — Intelligent chunking with metadata
3. **Initialize DB** — Create PostgreSQL table with indexes
4. **Embed & Ingest** — Store chunks + embeddings in pgvector
5. **Ask Questions** — Query and get answers with citations

**Example cells:**
```python
from config import *
from pdf_loader import read_pdf_text
from chunking import build_chunks
from embeddings import load_embedder, embed_chunks
from db import init_db, upsert_chunks

# 1. Load and chunk
text = read_pdf_text("Deep+Learning+Ian+Goodfellow.pdf")
chunks = build_chunks(text, EMBED_MODEL_NAME,
                      chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

# 2. Initialize database
init_db(PG_CONN_STR, EMBED_DIM)

# 3. Embed
embedder = load_embedder(EMBED_MODEL_NAME)
embeddings = embed_chunks(chunks, embedder)

# 4. Ingest
upsert_chunks(PG_CONN_STR, DOC_NAME, chunks, embeddings)

# 5. Ask
question = "What is backpropagation?"
# ... retrieve, rerank, generate ...
```

### Option 2: FastAPI Server (Production)

Start the API server:

```bash
uvicorn rag_api:app --reload --host 0.0.0.0 --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Option 3: Query via cURL/Python

#### Using cURL

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a convolutional neural network?"}'
```

#### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "Explain backpropagation in simple terms"}
)

data = response.json()
print(data["Generated Answer"])
print(data["Top Retrieved Chunks"])
# {
#   "Generated Answer": "Backpropagation is ...",
#   "Top Retrieved Chunks": [
#     { "section": "6.5_back_propagation", "content": "...",
#       "vector_similarity": 0.85, "final_score": 0.89 }
#   ]
# }
```

---

## 🔌 API Endpoints

### `POST /ask`

Ask the RAG system a question about the Deep Learning book.

**Request:**
```json
{
  "question": "What are the main components of a neural network?"
}
```

**Response:**
```json
{
  "Generated Answer": "The main components of a neural network are: ...",
  "Top Retrieved Chunks": [
    {
      "section": "6.1_example_feedforward_network",
      "content": "A feedforward neural network ...",
      "vector_similarity": 0.87,
      "final_score": 0.91
    }
  ]
}
```

**Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Empty question |
| 401 | HuggingFace authentication failed |
| 500 | Server error (missing API key, DB connection failed) |

---

## 📁 Project Structure

```
RAG - Book project/
├── README.md                      ← This file
├── requirements.txt               ← Python dependencies
├── .env.example                   ← Example environment config
├── .gitignore                     ← Git ignore rules
│
├── Deep+Learning+Ian+Goodfellow.pdf  ← Input PDF
├── Deep_Learning_Book.txt         ← Extracted text (reference)
│
├── config.py                      ← Central configuration hub
├── pdf_loader.py                  ← PDF extraction (PyMuPDF + pypdf fallback)
├── chunking.py                    ← Smart text chunking + cleaning
├── embeddings.py                  ← SentenceTransformer helpers
├── db.py                          ← PostgreSQL + pgvector operations
├── sql_queries.py                 ← SQL constants
├── retrieval.py                   ← Vector & hybrid search
├── rerank.py                      ← Post-retrieval reranking
├── query_expansion.py             ← Query synonym expansion
├── rag_api.py                     ← FastAPI server (/ask + /ingest)
├── evaluate_rag.py                ← Evaluation harness (10-query benchmark)
├── task1_run_baseline.py          ← Baseline retrieval script
│
├── fullsystem.ipynb               ← Full pipeline notebook (end-to-end)
├── fullsystem_1.ipynb             ← Alternative implementation
├── demo.ipynb                     ← Short demo notebook
├── task.ipynb                     ← Task-specific notebook
│
├── tests/
│   └── test_rag.py                ← Unit tests (pytest)
├── tmp_debug_schema.py            ← Debug script (optional)
└── system.png                     ← Architecture diagram
```

---

## 🔄 Complete Workflow Example

```python
import numpy as np
from openai import OpenAI

# 1. Load configuration
from config import *
from pdf_loader import read_pdf_text
from chunking import build_chunks
from embeddings import load_embedder, embed_chunks
from db import init_db, upsert_chunks, preview_chunks
from retrieval import retrieve_topk
from rerank import rerank_results
from rag_api import generate_text

# 2. Initialize everything
print("📚 Loading PDF...")
text = read_pdf_text("Deep+Learning+Ian+Goodfellow.pdf")

print("✂️  Chunking text...")
chunks = build_chunks(text, EMBED_MODEL_NAME,
                      chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
print(f"   → {len(chunks)} chunks created")

print("🗄️  Initializing database...")
init_db(PG_CONN_STR, EMBED_DIM)

print("🔎 Loading embedding model...")
embedder = load_embedder(EMBED_MODEL_NAME)

print("📊 Creating embeddings...")
embeddings = embed_chunks(chunks, embedder)

print("💾 Ingesting into pgvector...")
upsert_chunks(PG_CONN_STR, DOC_NAME, chunks, embeddings)
print(f"   → Stored {len(chunks)} chunk embeddings")

# 3. Ask a question
question = "What is the purpose of regularization?"
print(f"\n❓ Question: {question}")

# Embed query
qvec = embedder.encode([question], normalize_embeddings=True)[0]
qvec = np.asarray(qvec, dtype=np.float32)

# Retrieve top-20
raw_results = retrieve_topk(PG_CONN_STR, DOC_NAME, qvec, TOP_K_RETRIEVE)
print(f"   📤 Retrieved {len(raw_results)} candidates")

# Rerank to top-5
reranked = rerank_results(question, raw_results)
print(f"   ⭐ Reranked to top {min(TOP_K, len(reranked))}")

# Build context for LLM
context = "\n---\n".join([
    f"[{result[0]}]\n{result[1]}"
    for result in reranked[:TOP_K]
])

# Generate answer
client = OpenAI(base_url=HF_BASE_URL, api_key=HF_API_KEY)
answer = generate_text(client, context, question)
print(f"\n✅ Answer:\n{answer}")
```

---

## 🧪 Full System End-to-End Test

Run these commands in your project root:

```bash
# Install deps
pip install -r requirements.txt

# Initialize the DB and schema
python -c "from db import init_db; from config import PG_CONN_STR, EMBED_DIM; init_db(PG_CONN_STR, EMBED_DIM)"

# Ingest the book text with default chunking
python -c "from rag_api import ingest_document; import json; print(ingest_document({'source_path':'Deep_Learning_Book.txt','source_type':'text','chunk_size':450,'overlap':90}))"

# Run baseline query loop (local, stand-in for API) 
python task1_run_baseline.py

# Run evaluation harness
python evaluate_rag.py

# Run unit tests
pytest -q
```

## 🌐 API test examples

### 1. Ingest via endpoint:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_path":"Deep_Learning_Book.txt","source_type":"text","chunk_size":450,"overlap":90}'
```

### 2. Ask via endpoint:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain stochastic gradient descent."}'
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused to PostgreSQL"

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep pgvector

# If not running, start it
docker run --name pgvector-rag \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=online_rag_deeplearningbook \
  -p 5432:5432 \
  -d pgvector/pgvector:latest
```

### Issue: "ValueError: Embedding dimension mismatch"

**Solution:**
Ensure `EMBED_DIM` in `config.py` matches your model:
```python
# all-MiniLM-L6-v2 = 384 dimensions
EMBED_DIM = 384
```

### Issue: "Silent embedding truncation (no errors)"

**Solution:**
all-MiniLM-L6-v2 has a hard limit of 256 tokens. Keep `CHUNK_SIZE ≤ 220`:
```python
# ❌ Wrong (will truncate silently)
CHUNK_SIZE = 300

# ✅ Correct
CHUNK_SIZE = 220
```

### Issue: "No chunks retrieved (answer not found)"

**Diagnosis:** Check `DOC_NAME` in `config.py` matches what was ingested:
```python
# View ingested chunks
from db import preview_chunks
chunks = preview_chunks(PG_CONN_STR, limit=3)
print(chunks)

# Should show your DOC_NAME in output
```

### Issue: "HF API key missing or invalid"

**Solution:**
```bash
# Add to .env
echo "HF_API_KEY=hf_..." >> .env

# Or set environment variable directly
export HF_API_KEY=hf_...
```

### Issue: "Slow retrieval (>5 seconds)"

**Solution:**
Ensure pgvector indexes are created:
```python
from db import init_db
from config import PG_CONN_STR, EMBED_DIM
init_db(PG_CONN_STR, EMBED_DIM)
# This creates HNSW indexes automatically
```

---

## 🎓 Learning Resources

- **Chunking Strategy** — See `chunking.py` docstring for regex analysis
- **Page Tracking** — Form-feed (`\f`) separators in `pdf_loader.py`
- **Embedding Models** — [Sentence-Transformers](https://www.sbert.net/)
- **PostgreSQL + pgvector** — [pgvector docs](https://github.com/pgvector/pgvector)
- **FastAPI** — [Official docs](https://fastapi.tiangolo.com/)
- **RAG Pattern** — [Langchain RAG](https://python.langchain.com/docs/use_cases/question_answering/)

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Total Chunks | ~2,500 |
| Avg Chunk Size | ~220 tokens |
| Embedding Vector Dim | 384 |
| Vector Search (top-20) | ~50ms |
| Reranking (20→5) | ~10ms |
| LLM Generation | ~1-2s |
| **Total Latency** | **~1.5-2.5s** |

---

## 🔐 Security Notes

1. **Never commit `.env` file** — It contains API keys
   ```bash
   # .gitignore already includes:
   .env
   .env.local
   .env.*.local
   ```

2. **Use environment variables in production:**
   ```python
   import os
   api_key = os.getenv("HF_API_KEY")
   ```

3. **Rotate API keys regularly** — Especially if exposed

---

## 🚀 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Set up PostgreSQL: See "Prerequisites" section
3. ✅ Configure `.env` file
4. ✅ Run notebook: `jupyter notebook fullsystem.ipynb`
5. ✅ Start API: `uvicorn rag_api:app --reload`
6. ✅ Test `/ask` endpoint

---

## 🤝 Contributing

Issues & PRs welcome! Areas for enhancement:

- [ ] Multi-document support (beyond one book)
- [ ] Semantic caching to reduce LLM calls
- [ ] Fine-tuned embedding models
- [ ] Web UI for chat interface
- [ ] Persisted conversation history
- [ ] Advanced filtering (by chapter, by year, etc.)

---

## 📜 License

MIT License — Free to use, modify, distribute.

---

## 📞 Support

**Issues?** Check the troubleshooting section above.

**Questions?** Review the docstrings in each module:
- `config.py` — Configuration explained
- `chunking.py` — Regex logic & boilerplate filtering
- `rag_api.py` — API endpoints & LLM prompting
- `db.py` — Database schema & operations

---

## 📅 Changelog

### v2.0 (Current)
- ✅ Fixed reranking tuple index mismatch (was producing wrong scores)
- ✅ Fixed import errors in `rag_api.py` (startup crash)
- ✅ Fixed `preview_chunks` column unpacking (runtime crash)
- ✅ Removed duplicate `hybrid_retrieve_topk` function
- ✅ Added `load_dotenv()` — `.env` files now actually loaded
- ✅ Set `CHUNK_SIZE=220` / `MAX_MODEL_TOKENS=256` for safe embedding
- ✅ Python 3.9 compatibility (`Optional[int]` instead of `int | None`)
- ✅ Cleaned unused imports across modules
- ✅ Created `.env.example` template
- ✅ README corrected to match actual API and function signatures

### v1.0
- ✅ Smart chunking with section detection
- ✅ Page tracking for citations
- ✅ Hybrid (vector + keyword) search
- ✅ Two-stage retrieval + reranking
- ✅ FastAPI server with `/ask` endpoint
- ✅ Full Jupyter notebooks included

---

**Happy RAG-ing! 🚀📚**
