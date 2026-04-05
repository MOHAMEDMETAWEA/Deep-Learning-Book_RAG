
import psycopg
from pgvector.psycopg import register_vector
import numpy as np

def reproduce_error():
    conn_str = "postgresql://postgres:admin@localhost:5432/online_rag_deeplearningbook"
    try:
        with psycopg.connect(conn_str) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                # Use current query
                SQL = """
SELECT
    chapter, section, chunk_index, content,
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
                query_vec = np.random.rand(384).astype(np.float32)
                params = (query_vec, "test", "DeepLearning-IanGoodfellow_RAG", None, None, 5)
                
                print("Executing query with params...")
                cur.execute(SQL, params)
                print("Success!")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    reproduce_error()
