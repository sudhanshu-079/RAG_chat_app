import faiss
import numpy as np
import os


def save_faiss_index(embeddings, index_path):
    """
    embeddings: NumPy array (num_chunks, dim)
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype("float32"))

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)

    return index_path


def retrieve_chunks(index_path, query_embedding, chunks, k=5):
    """
    index_path: path to FAISS index
    query_embedding: NumPy array (1, dim)
    chunks: list of original text chunks
    """

    index = faiss.read_index(index_path)

    # Convert query embedding properly
    if isinstance(query_embedding, list):
        query_embedding = np.array(query_embedding)

    query_embedding = np.array(query_embedding).astype("float32")

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    k = min(k, index.ntotal)

    D, I = index.search(query_embedding, k)

    return [chunks[i] for i in I[0]]