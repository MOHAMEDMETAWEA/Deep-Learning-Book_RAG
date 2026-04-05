"""evaluate_rag.py

Evaluation harness for RAG system.

Metrics:
- retrieval_accuracy (top1 contains expected target phrase)
- citation_correctness (chapter metadata presence)
- answer_faithfulness (placeholder; using keyword overlap in generated answer)
"""
from typing import List, Dict

from config import PG_CONN_STR, DOC_NAME, TOP_K_RETRIEVE
from embeddings import load_embedder
from retrieval import retrieve_topk
from rerank import rerank_results


def evaluate_queries(queries: List[Dict]):
    embedder = load_embedder('sentence-transformers/all-MiniLM-L6-v2')
    results = []

    for q in queries:
        question = q['question']
        expected = q['expected']

        qvec = embedder.encode([question], normalize_embeddings=True)[0]
        raw = retrieve_topk(PG_CONN_STR, DOC_NAME, qvec, TOP_K_RETRIEVE)
        reranked = rerank_results(question, raw)

        top = reranked[0] if reranked else None
        top_content = top[1] if top else ""
        top_score = top[3] if top else 0.0

        retrieval_accuracy = 1.0 if expected.lower() in top_content.lower() else 0.0
        citation_correctness = 1.0 if top and top[0] else 0.0

        answer_faithfulness = 1.0 if expected.lower().split()[0] in top_content.lower() else 0.0

        results.append({
            'question': question,
            'expected': expected,
            'retrieval_accuracy': retrieval_accuracy,
            'citation_correctness': citation_correctness,
            'answer_faithfulness': answer_faithfulness,
            'top_chunk': top_content[:250],
            'top_score': top_score,
        })

    return results


if __name__ == '__main__':
    test_queries = [
        { 'question': 'What is stochastic gradient descent?', 'expected': 'stochastic gradient descent' },
        { 'question': 'Define convolutional neural network', 'expected': 'convolutional neural network' },
        { 'question': 'How does batch normalization work?', 'expected': 'batch normalization' },
        { 'question': 'Explain vanishing gradient problem', 'expected': 'vanishing gradient' },
        { 'question': 'What is the role of the loss function?', 'expected': 'loss function' },
        { 'question': 'How does dropout regularization help?', 'expected': 'dropout' },
        { 'question': 'Define overfitting in deep learning', 'expected': 'overfitting' },
        { 'question': 'What is the Adam optimizer?', 'expected': 'Adam' },
        { 'question': 'Explain backpropagation', 'expected': 'backpropagation' },
        { 'question': 'What are activation functions?', 'expected': 'activation function' },
    ]

    output = evaluate_queries(test_queries)
    for r in output:
        print(r)

    avg_retrieval = sum(r['retrieval_accuracy'] for r in output) / len(output)
    avg_citation = sum(r['citation_correctness'] for r in output) / len(output)
    avg_faithfulness = sum(r['answer_faithfulness'] for r in output) / len(output)

    print('---')
    print(f'Avg retrieval accuracy: {avg_retrieval:.2f}')
    print(f'Avg citation correctness: {avg_citation:.2f}')
    print(f'Avg answer faithfulness (proxy): {avg_faithfulness:.2f}')
