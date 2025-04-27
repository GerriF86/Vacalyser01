# src/utils/vector_store.py
import os
import faiss
import numpy as np
import pickle
from typing import List
from openai_utils import OpenAIUtils

VECTOR_BASE_DIR = "vector_bases"
INDEX_FILE = os.path.join(VECTOR_BASE_DIR, "job_index.faiss")
DATA_FILE = os.path.join(VECTOR_BASE_DIR, "job_vectors.pkl")

def ensure_dirs():
    if not os.path.exists(VECTOR_BASE_DIR):
        os.makedirs(VECTOR_BASE_DIR)

def init_index(dim: int = 1536):
    """
    Initialize a new FAISS index for given dimension.
    """
    index = faiss.IndexFlatL2(dim)  # flat (exact) index
    return index

def save_index(index, metadata):
    """
    Save FAISS index and metadata vectors.
    """
    ensure_dirs()
    faiss.write_index(index, INDEX_FILE)
    with open(DATA_FILE, "wb") as f:
        pickle.dump(metadata, f)

def load_index():
    """
    Load existing FAISS index and metadata if present.
    Returns (index, metadata) or (None, None).
    """
    try:
        index = faiss.read_index(INDEX_FILE)
        with open(DATA_FILE, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata
    except Exception:
        return None, []

def add_to_index(text: str, metadata_item):
    """
    Embed text and add to index with associated metadata.
    """
    ensure_dirs()
    openai = OpenAIUtils()
    emb_response = openai.chat_completion(
        prompt=f"Embed this text for vector indexing:\n{text}",
        system_message="You are an embedding generator."
    )
    # If using real embeddings, use OpenAI embedding API:
    # embeddings = get_openai_embeddings(text)
    # But here we simulate with ChatCompletion for example (not real).
    try:
        vector = np.fromstring(emb_response.replace("[", "").replace("]", ""), sep=",")
    except Exception:
        vector = np.random.rand(1536).astype('float32')  # fallback random
    vector = np.array([vector], dtype='float32')

    idx, metadata = load_index()
    if idx is None:
        idx = init_index(dim=len(vector[0]))
        metadata = []
    idx.add(vector)
    metadata.append(metadata_item)
    save_index(idx, metadata)

def query_index(query: str, top_k: int = 5) -> List:
    """
    Query the FAISS index for nearest entries to the query text.
    """
    idx, metadata = load_index()
    if idx is None:
        return []
    openai = OpenAIUtils()
    emb_response = openai.chat_completion(
        prompt=f"Embed this query for vector search:\n{query}",
        system_message="You are an embedding generator."
    )
    try:
        qvec = np.fromstring(emb_response.replace("[", "").replace("]", ""), sep=",")
    except Exception:
        qvec = np.random.rand(1536).astype('float32')
    qvec = np.array([qvec], dtype='float32')

    distances, indices = idx.search(qvec, top_k)
    results = []
    for i in indices[0]:
        if i < len(metadata):
            results.append(metadata[i])
    return results
