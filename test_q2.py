import os
from config import PG_CONN_STR, DOC_NAME, EMBED_MODEL_NAME
from embeddings import load_embedder
from retrieval import retrieve_topk, hybrid_retrieve_topk

embedder = load_embedder(EMBED_MODEL_NAME)
queries = [
    "define artificial neural network",
    "explain what a neural network is",
    "deep feedforward networks",
    "what are feedforward neural networks"
]

with open("test_q_out2.txt", "w", encoding="utf-8") as f:
    for q in queries:
        qvec = embedder.encode([q], normalize_embeddings=True)[0]
        results = hybrid_retrieve_topk(PG_CONN_STR, DOC_NAME, qvec, q, 5)
        f.write(f"\n--- QUERY: {q} ---\n")
        f.write(f"Num results: {len(results)}\n")
        for r in results:
            content = r[3].replace("\n", " ").strip()
            f.write(f"[{r[1]}] Score: {r[4]:.4f} | Content: {content[:200]}...\n")
