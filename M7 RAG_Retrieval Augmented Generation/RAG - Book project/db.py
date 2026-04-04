"""
db.py
─────
PostgreSQL + pgvector database helpers.

CHANGES vs. original
─────────────────────
① upsert_chunks now writes chapter + section (schema updated in sql_queries.py).
② INSERT_CHUNK_SQL now has 6 placeholders — old code passed 5, causing
   "too many columns" or "not enough values" psycopg errors.
③ PREVIEW uses parameterised limit (no more module-level constant baked in).
④ DELETE functions split into delete_all_chunks / delete_doc_chunks so you
   can wipe a single document without nuking the whole table.
⑤ Imports cleaned — psycopg was re-imported inside functions unnecessarily.
"""

import psycopg
from pgvector.psycopg import register_vector

from sql_queries import (
    INSERT_CHUNK_SQL,
    PREVIEW_CHUNKS_SQL,
    COUNT_CHUNKS_SQL,
    COUNT_DOC_CHUNKS_SQL,
    get_create_chunks_table_sql,
    DELETE_ALL_CHUNKS_SQL,
    DELETE_DOC_CHUNKS_SQL,
)


# ─────────────────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────────────────

def init_db(conn_str: str, dim: int):
    """Create rag_cv_chunks table and indexes if they don't exist.

    Also add missing columns for existing older schema versions.
    """
    SCHEMA_VERSION = 2

    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            # Ensure pgvector extension exists before table operations
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            register_vector(conn)

            # Create schema version table + ensure version row exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id SERIAL PRIMARY KEY,
                    version INT NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)
            cur.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1;")
            row = cur.fetchone()
            if row is None:
                cur.execute("INSERT INTO schema_version (version) VALUES (%s)", (SCHEMA_VERSION,))
            elif row[0] < SCHEMA_VERSION:
                cur.execute("UPDATE schema_version SET version = %s, updated_at = NOW()", (SCHEMA_VERSION,))

            # Create table if not exists (initial schema for new installs)
            cur.execute(get_create_chunks_table_sql(dim))

            # Migration path: add newly introduced columns if absent
            cur.execute("ALTER TABLE rag_cv_chunks ADD COLUMN IF NOT EXISTS chapter TEXT;")
            cur.execute("ALTER TABLE rag_cv_chunks ADD COLUMN IF NOT EXISTS section TEXT;")
            cur.execute("ALTER TABLE rag_cv_chunks ADD COLUMN IF NOT EXISTS chunk_index INT;")
            cur.execute("ALTER TABLE rag_cv_chunks ADD COLUMN IF NOT EXISTS content TEXT;")
            cur.execute("ALTER TABLE rag_cv_chunks ADD COLUMN IF NOT EXISTS embedding VECTOR({});".format(dim))

            # Set up full-text vector for hybrid search (PostgreSQL 12+)
            cur.execute("ALTER TABLE rag_cv_chunks ADD COLUMN IF NOT EXISTS content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED;")

            # Ensure indexes exist as well
            cur.execute("CREATE INDEX IF NOT EXISTS rag_cv_chunks_doc_idx ON rag_cv_chunks (doc_name);")
            cur.execute("CREATE INDEX IF NOT EXISTS rag_cv_chunks_hnsw_idx ON rag_cv_chunks USING hnsw (embedding vector_cosine_ops);")
            cur.execute("CREATE INDEX IF NOT EXISTS rag_cv_chunks_content_tsv_idx ON rag_cv_chunks USING gin(content_tsv);")

        conn.commit()
    print(f"✅ DB initialised — embedding dim={dim}, schema version={SCHEMA_VERSION}")


# ─────────────────────────────────────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────────────────────────────────────

def upsert_chunks(conn_str: str, doc_name: str, chunks: list, vectors):
    """
    Insert chunks + their embeddings into the database.

    Parameters
    ----------
    conn_str : str    PostgreSQL connection string.
    doc_name : str    Identifier for this document (used for retrieval scoping).
    chunks   : list   List of chunk dicts from build_chunks().
                      Expected keys: chapter, section, content.
    vectors  : array  Numpy array of shape (N, embed_dim).
    """
    with psycopg.connect(conn_str) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
                cur.execute(
                    INSERT_CHUNK_SQL,
                    (
                        doc_name,
                        chunk.get("chapter", ""),
                        chunk.get("section", ""),
                        i,
                        chunk.get("content", ""),
                        vec,
                    ),
                )
        conn.commit()
    print(f"💾 Stored {len(chunks)} chunks for '{doc_name}'")


# ─────────────────────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────────────────────

def delete_all_chunks(conn_str: str):
    """Delete every row from rag_cv_chunks (all documents)."""
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_ALL_CHUNKS_SQL)
        conn.commit()
    print("🗑️  All chunks deleted from rag_cv_chunks")


def delete_doc_chunks(conn_str: str, doc_name: str):
    """Delete only the chunks belonging to a specific document."""
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_DOC_CHUNKS_SQL, (doc_name,))
        conn.commit()
    print(f"🗑️  Chunks deleted for doc '{doc_name}'")


# ─────────────────────────────────────────────────────────────────────────────
# INSPECT
# ─────────────────────────────────────────────────────────────────────────────

def count_chunks(conn_str: str, doc_name: str = None) -> int:
    """Return total chunk count (or count for a specific doc if given)."""
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            if doc_name:
                cur.execute(COUNT_DOC_CHUNKS_SQL, (doc_name,))
            else:
                cur.execute(COUNT_CHUNKS_SQL)
            count = cur.fetchone()[0]
    label = f"'{doc_name}'" if doc_name else "total"
    print(f"📦 Chunks ({label}): {count}")
    return count


def preview_chunks(conn_str: str, limit: int = 5):
    """Print a sample of stored chunks."""
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(PREVIEW_CHUNKS_SQL, (limit,))
            rows = cur.fetchall()

    print("\n🔎 Stored Chunks Preview\n")
    for doc, sec, content in rows:
        print(f"DOC:     {doc}")
        print(f"SECTION: {sec}")
        print(content[:200])
        print("-" * 40)