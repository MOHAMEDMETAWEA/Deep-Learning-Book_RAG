import os
from config import PG_CONN_STR, DOC_NAME, EMBED_MODEL_NAME
from embeddings import load_embedder
from retrieval import retrieve_topk, hybrid_retrieve_topk
from query_expansion import expand_query

embedder = load_embedder(EMBED_MODEL_NAME)
queries = ["what is neural network", "what is NN", "what is neaural network", "what is a neural network?"]

with open("test_q_out.txt", "w", encoding="utf-8") as f:
    for q in queries:
        expanded = expand_query(q)["expanded"]
        qvec = embedder.encode([expanded], normalize_embeddings=True)[0]
        results = hybrid_retrieve_topk(PG_CONN_STR, DOC_NAME, qvec, expanded, 5)
        f.write(f"\n--- QUERY: {q} (Expanded: {expanded}) ---\n")
        f.write(f"Num results: {len(results)}\n")
        for r in results:
            content = r[3].replace("\n", " ").strip()
            f.write(f"[{r[1]}] Score: {r[4]:.4f} | Content: {content[:150]}...\n")
