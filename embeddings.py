"""
embeddings.py
─────────────
SentenceTransformer embedding helpers.

CHANGES vs. original
─────────────────────
① embed_chunks now accepts either List[str] or List[dict] (with 'content' key).
   Original only worked with plain strings — if you passed chunk dicts directly
   (easy mistake when calling from a notebook) it would embed repr() strings.
② show_progress_bar added for long ingestion jobs (800-page book).
③ normalize_embeddings=True kept — ensures cosine similarity = dot product,
   which is required for pgvector's <=> operator to give correct scores.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union


def load_embedder(model_name: str) -> SentenceTransformer:
    """Load and return the SentenceTransformer model."""
    print(f"🔎 Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    return model


def embed_chunks(
    chunks: Union[List[str], List[dict]],
    embedder: SentenceTransformer,
    batch_size: int = 32,
) -> np.ndarray:
    """
    Embed a list of text strings or chunk dicts.

    Parameters
    ----------
    chunks    : List[str] or List[dict]
                Either plain strings or dicts with a 'content' key.
    embedder  : SentenceTransformer   Loaded model.
    batch_size: int                   Encoding batch size.

    Returns
    -------
    np.ndarray of shape (N, embed_dim), dtype=float32, L2-normalised.
    """
    # Accept both plain strings and chunk dicts
    if chunks and isinstance(chunks[0], dict):
        texts = [c["content"] for c in chunks]
    else:
        texts = list(chunks)

    vecs = embedder.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return np.asarray(vecs, dtype=np.float32)