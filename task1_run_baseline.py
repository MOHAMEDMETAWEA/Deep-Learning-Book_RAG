"""Task 1: Baseline retrieval + generation run for deep learning questions."""
import os
import sys

from config import CHUNK_SIZE, CHUNK_OVERLAP
from chunking import read_bdf_text, build_chunks
from embeddings import load_embedder, embed_chunks

try:
    from sklearn.neighbors import NearestNeighbors
except ImportError:
    NearestNeighbors = None


QUESTIONS = [
    "What is stochastic gradient descent?",
    "Describe the vanishing gradient problem.",
    "What is a convolutional neural network?",
    "Explain dropout regularization.",
    "What is batch normalization?",
    "How does weight decay work?",
    "What are activation functions used for?",
    "Define the loss function.",
    "How can overfitting be prevented?",
    "What does backpropagation do?",
]


def main():
    path = "Deep_Learning_Book.txt"
    if not os.path.exists(path):
        print("ERROR: Book text file not found", path)
        sys.exit(1)

    raw_text = read_bdf_text(path)
    chunks = build_chunks(raw_text, 'sentence-transformers/all-MiniLM-L6-v2', chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

    print(f"Baseline chunks created: {len(chunks)}")

    embedder = load_embedder('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = embed_chunks(chunks, embedder)

    if NearestNeighbors is None:
        raise RuntimeError("Install scikit-learn to run the baseline retrieval script")

    nn = NearestNeighbors(n_neighbors=5, metric='cosine').fit(embeddings)

    for question in QUESTIONS:
        qvec = embedder.encode([question], normalize_embeddings=True)[0]
        dists, idxs = nn.kneighbors([qvec], n_neighbors=5, return_distance=True)

        print("\nQuestion:", question)
        print("Answer (pseudo, from top chunk):")
        top_chunk = chunks[idxs[0][0]]
        print(top_chunk['content'][:512].replace('\n', ' '))
        print("Retrieved Chunks:")
        for rank, i in enumerate(idxs[0]):
            c = chunks[i]
            print(f"  - Rank {rank+1}, section={c['section']}, chapter={c['chapter']}, tokens={c['token_len']}")


if __name__ == '__main__':
    main()
