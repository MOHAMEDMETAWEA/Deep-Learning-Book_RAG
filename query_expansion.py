"""query_expansion.py

Simple query expansion support for RAG pipeline.
"""
import re

SYNONYMS = {
    "sgd": "stochastic gradient descent",
    "cnn": "convolutional neural network",
    "rnn": "recurrent neural network",
    "adam": "adaptive moment estimation",
    "lstm": "long short-term memory",
    "optimizer": "optimization algorithm",
    "nn": "neural network",
}


def expand_query(query: str) -> dict:
    """Expand query in two ways:

    1. LLM-like rewrite (simple heuristic placeholder for offline invocation)
    2. keyword synonym injection

    Returns:
       {"original": ..., "expanded": ..., "expansion_tokens": ...}
    """
    normalized = query.strip()

    lower = normalized.lower()
    expanded_tokens = []
    for token in re.findall(r"\b\w+\b", lower):
        expanded_tokens.append(token)
        if token in SYNONYMS:
            expanded_tokens.extend(SYNONYMS[token].split())

    expanded = " ".join(dict.fromkeys(expanded_tokens))

    # simulated LLM rewrite (safe deterministic)
    rewrite_map = {
        "sgd": "explain stochastic gradient descent optimization algorithm",
        "cnn": "explain convolutional neural network architecture",
        "backpropagation": "explain backpropagation algorithm",
    }
    prompt = ""
    for key, value in rewrite_map.items():
        if key in lower:
            prompt = value
            break

    if not prompt:
        prompt = "Explain " + normalized

    return {
        "original": normalized,
        "expanded": expanded,
        "rewrite": prompt,
    }
