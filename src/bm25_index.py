from pathlib import Path
import pickle

from langchain_community.retrievers import BM25Retriever


STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_FILE = Path("C:/Users/SridharS/Downloads/Sridhar_Project/agri-claimguard-agentic-rag/storage/chunks.pkl")

def save_chunks(chunks):
    """Persist chunk documents for rebuilding the BM25 index."""
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(chunks, f)


def load_chunks():
    """Load previously saved chunk documents."""
    with open(CHUNKS_FILE, "rb") as f:
        return pickle.load(f)


def create_bm25_index(chunks, k: int = 5):
    save_chunks(chunks)

    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = k

    return bm25

def get_bm25_index(k: int = 5):
    """
    Load the persisted chunks and rebuild the BM25 index.
    """

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            "BM25 index not found. Run the ingestion pipeline first."
        )

    chunks = load_chunks()

    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = k

    return bm25