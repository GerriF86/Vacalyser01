#rag_helpers.py

import os
import pickle
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env
INDEX_PATH = "vector_databases/index.faiss"
MAPPING_PATH = "vector_databases/index.pkl"

EMBEDDING_MODEL = None
FAISS_INDEX = None
INDEX_LOADED = False

def init_faiss_index():
    """
    One-time load of the embedding model 
    and the FAISS index from local disk.
    """
    global EMBEDDING_MODEL, FAISS_INDEX, INDEX_LOADED
    if EMBEDDING_MODEL is None:
        EMBEDDING_MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    if not INDEX_LOADED and os.path.exists(INDEX_PATH):
        FAISS_INDEX = faiss.read_index(INDEX_PATH)
        INDEX_LOADED = True

def search_faiss(query:str, top_k=3):
    """
    Encodes the query using our model, 
    does a top_k search in the FAISS index,
    retrieves matching docs from the mapping.
    """
    init_faiss_index()
    if not FAISS_INDEX or EMBEDDING_MODEL is None:
        st.warning("FAISS index or embedding model not loaded.")
        return []

    q_emb = EMBEDDING_MODEL.encode([query]).astype(np.float32)
    distances, indices = FAISS_INDEX.search(q_emb, top_k)

    if not os.path.exists(MAPPING_PATH):
        st.warning("Index mapping file not found.")
        return []

    with open(MAPPING_PATH,"rb") as f:
        mapping = pickle.load(f)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        key = str(idx)
        if key in mapping:
            doc_info = mapping[key]
            doc_info["distance"] = float(dist)
            results.append(doc_info)
    return results
