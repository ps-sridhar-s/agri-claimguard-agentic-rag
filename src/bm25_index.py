from pathlib import Path
import pickle

from langchain_community.retrievers import BM25Retriever


STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_chunks(chunks):
    """Persist chunk documents for rebuilding the BM25 index."""
    with open(STORAGE_DIR / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)


def load_chunks():
    """Load previously saved chunk documents."""
    with open(STORAGE_DIR / "chunks.pkl", "rb") as f:
        return pickle.load(f)


def create_bm25_index(chunks, k: int = 5):
    save_chunks(chunks)

    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = k

    return bm25