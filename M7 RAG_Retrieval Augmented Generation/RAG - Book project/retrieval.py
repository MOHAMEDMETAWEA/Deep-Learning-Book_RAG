"""
retrieval.py
────────────
Vector search and hybrid search against pgvector.

CHANGES vs. original
─────────────────────
① Added hybrid_retrieve_topk for Task 5 (keyword + vector blended search).
② Added ::vector cast explicitly to satisfy strict pgvector typing.
③ Imports centralised — no more scattered inline imports.
"""

import psycopg
from pgvector.psycopg import register_vector

from sql_queries import SEARCH_CHUNKS_SQL, HYBRID_SEARCH_SQL


def retrieve_topk(conn_str: str, doc_name: str, query_vec, k: int) -> list:
    """
    Pure vector search.

    Returns list of tuples: (chapter, section, chunk_index, content, cosine_sim)
    """
    with psycopg.connect(conn_str) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(SEARCH_CHUNKS_SQL, (query_vec, doc_name, query_vec, k))
            rows = cur.fetchall()
    return rows


def hybrid_retrieve_topk(
    conn_str: str,
    doc_name: str,
    query_vec,
    query_text: str,
    k: int,
) -> list:
    """
    Hybrid search: 70 % vector similarity + 30 % PostgreSQL full-text rank.

    Returns list of tuples:
      (chapter, section, chunk_index, content, hybrid_score)
    """
    with psycopg.connect(conn_str) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                HYBRID_SEARCH_SQL,
                (query_vec, query_text, doc_name, k),
            )
            rows = cur.fetchall()
    return rows


def hybrid_retrieve_topk(
    conn_str: str,
    doc_name: str,
    query_vec,
    query_text: str,
    k: int,
) -> list:
    """
    Hybrid search: 70 % vector similarity + 30 % PostgreSQL full-text rank.

    Returns list of 3-tuples: (section, content, hybrid_score)

    Use this for technical term queries like "SGD", "CNN", "backpropagation"
    where exact keyword presence matters alongside semantic similarity.
    """
    with psycopg.connect(conn_str) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                HYBRID_SEARCH_SQL,
                (query_vec, query_text, doc_name, k),
            )
            rows = cur.fetchall()
    return rows