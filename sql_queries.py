"""
sql_queries.py
──────────────
All SQL used by db.py and retrieval.py.

CHANGES vs. original
─────────────────────
① Added `chapter` column to the table schema (Task 4 metadata requirement).
② SEARCH query now returns cosine_sim correctly — pgvector <=> is distance,
   so similarity = 1 - distance. Column order matches _normalize_row() in
   rag_api.py and the HTML unpacker in fullsystem.ipynb.
③ Added HYBRID_SEARCH_SQL that blends vector + full-text (ts_vector) scores
   (Task 5 — hybrid search).
④ Fixed PREIVEW_CHUNKS_SQL (typo in original: PREIVEW) and made limit a
   parameter instead of a module-level baked-in constant.
⑤ Separated DELETE per doc vs. DELETE all for safer operations.
"""


# ─────────────────────────────────────────────────────────────────────────────
# TABLE CREATION
# ─────────────────────────────────────────────────────────────────────────────

def get_create_chunks_table_sql(dim: int) -> str:
    return f"""
CREATE TABLE IF NOT EXISTS rag_cv_chunks (
    id          SERIAL PRIMARY KEY,
    doc_name    TEXT NOT NULL,
    chapter     TEXT,
    section     TEXT,
    chunk_index INT NOT NULL,
    content     TEXT,
    embedding   VECTOR({dim}),
    UNIQUE(doc_name, chunk_index)
);
"""


def get_create_indexes_sql() -> str:
    """Return index creation SQL — call AFTER all migrations have run."""
    return """
CREATE UNIQUE INDEX IF NOT EXISTS rag_cv_chunks_doc_chunk_uidx
    ON rag_cv_chunks (doc_name, chunk_index);

CREATE INDEX IF NOT EXISTS rag_cv_chunks_doc_idx
    ON rag_cv_chunks (doc_name);

CREATE INDEX IF NOT EXISTS rag_cv_chunks_hnsw_idx
    ON rag_cv_chunks
    USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS rag_cv_chunks_content_tsv_idx
    ON rag_cv_chunks
    USING gin(content_tsv);
"""


# ─────────────────────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────────────────────

INSERT_CHUNK_SQL = """
INSERT INTO rag_cv_chunks
    (doc_name, chapter, section, chunk_index, content, embedding)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (doc_name, chunk_index)
DO UPDATE SET
    chapter = EXCLUDED.chapter,
    section = EXCLUDED.section,
    content = EXCLUDED.content,
    embedding = EXCLUDED.embedding;
"""


# ─────────────────────────────────────────────────────────────────────────────
# VECTOR SEARCH   →  returns (section, content, cosine_sim)
# ─────────────────────────────────────────────────────────────────────────────

SEARCH_CHUNKS_SQL = """
SELECT
    chapter,
    section,
    chunk_index,
    content,
    1 - (embedding <=> %s::vector)  AS cosine_sim
FROM  rag_cv_chunks
WHERE doc_name = %s
ORDER BY embedding <=> %s::vector
LIMIT %s
"""


# ─────────────────────────────────────────────────────────────────────────────
# HYBRID SEARCH  (vector + PostgreSQL full-text)  →  (section, content, score)
# ─────────────────────────────────────────────────────────────────────────────
# Usage: pass (query_vec, doc_name, query_text, query_vec, top_k)
# The ts_rank score is normalised to [0,1] via LEAST(..., 1).

HYBRID_SEARCH_SQL = """
SELECT
    chapter,
    section,
    chunk_index,
    content,
    0.7 * (1 - (embedding <=> %s::vector))
    + 0.3 * LEAST(ts_rank(to_tsvector('english', content),
                            plainto_tsquery('english', %s)), 1)
    AS hybrid_score
FROM  rag_cv_chunks
WHERE doc_name = %s
  AND (COALESCE(%s::TEXT[], '{}') = '{}' OR chapter = ANY(%s::TEXT[]))
ORDER BY hybrid_score DESC
LIMIT %s
"""

LIST_CHAPTERS_SQL = "SELECT DISTINCT chapter FROM rag_cv_chunks WHERE doc_name = %s ORDER BY chapter;"


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────────────────────

DELETE_ALL_CHUNKS_SQL  = "DELETE FROM rag_cv_chunks;"
DELETE_DOC_CHUNKS_SQL  = "DELETE FROM rag_cv_chunks WHERE doc_name = %s;"
COUNT_CHUNKS_SQL       = "SELECT COUNT(*) FROM rag_cv_chunks;"
COUNT_DOC_CHUNKS_SQL   = "SELECT COUNT(*) FROM rag_cv_chunks WHERE doc_name = %s;"

PREVIEW_CHUNKS_SQL = """
SELECT doc_name, chapter, section, chunk_index, content
FROM   rag_cv_chunks
LIMIT  %s
"""