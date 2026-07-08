import time
from pathlib import Path

from langchain_core.documents import Document

from models.embeddings_models import embedding_client
from src.vector_storage import get_vectorstore
from src.bm25_index import get_bm25_index

STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

CHUNKS_FILE = STORAGE_DIR / "chunks.pkl"


class HybridRetriever:
    def __init__(self, semantic_retriever, sparse_retriever, rrf_k: int = 60):
        self.semantic_retriever = semantic_retriever
        self.sparse_retriever = sparse_retriever
        self.rrf_k = rrf_k

    def invoke(self, query: str):
        semantic_docs = self.semantic_retriever.invoke(query)
        sparse_docs = self.sparse_retriever.invoke(query)

        return reciprocal_rank_fusion(semantic_docs, sparse_docs, rrf_k=self.rrf_k)


def _document_key(doc: Document):
    source = doc.metadata.get("source") if isinstance(doc.metadata, dict) else None

    return source, doc.page_content


def reciprocal_rank_fusion(*document_groups, rrf_k: int = 60):
    scores = {}
    documents_by_key = {}

    for documents in document_groups:
        for rank, doc in enumerate(documents, start=1):
            key = _document_key(doc)
            documents_by_key.setdefault(key, doc)
            scores[key] = scores.get(key, 0.0) + 1.0 / (rrf_k + rank)

    ranked_keys = sorted(
        scores,
        key=lambda key: (-scores[key], documents_by_key[key].page_content),
    )

    return [documents_by_key[key] for key in ranked_keys]


def build_hybrid_retriever(vectorstore, bm25_index, k: int = 5, rrf_k: int = 60):
    semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    if hasattr(bm25_index, "k"):
        bm25_index.k = k

    return HybridRetriever(semantic_retriever, bm25_index, rrf_k=rrf_k)


def _is_loaded_state(state) -> bool:
    state_value = state.get("state") if isinstance(state, dict) else state
    state_name = getattr(state_value, "name", str(state_value))

    return state_name.lower() == "loaded" or str(state_value) == "3"


def _load_collection_for_search(
    client,
    collection_name: str,
    timeout_seconds: float = 5.0,
) -> None:
    client.load_collection(collection_name)

    if not hasattr(client, "get_load_state"):
        return

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if _is_loaded_state(client.get_load_state(collection_name)):
            return
        time.sleep(0.1)


def _is_released_collection_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "state 'released'" in message and "call load()" in message


def _search_loaded_collection(client, collection_name: str, query_embedding, k: int):
    _load_collection_for_search(client, collection_name)

    try:
        return client.search(
            collection_name=collection_name,
            data=[query_embedding],
            limit=k,
            output_fields=["text", "metadata"],
        )
    except Exception as exc:
        if not _is_released_collection_error(exc):
            raise

        _load_collection_for_search(client, collection_name)
        return client.search(
            collection_name=collection_name,
            data=[query_embedding],
            limit=k,
            output_fields=["text", "metadata"],
        )


def semantic_search(
    query: str,
    k: int = 5,
    collection_name: str = "crop_insurance",
):
    client = get_vectorstore()

    query_embedding = embedding_client.embed_query(query)

    results = _search_loaded_collection(client, collection_name, query_embedding, k)

    documents = []

    for hit in results[0]:

        entity = hit["entity"]

        documents.append(
            Document(
                page_content=entity["text"],
                metadata=entity.get("metadata", {}),
            )
        )

    return documents


def hybrid_retriever(
    query: str,
    semantic_weight: float = 0.7,
    sparse_weight: float = 0.3,
    k: int = 5,
    rrf_k: int = 60,
):
    """
    Simple Hybrid Retrieval
    """

    if not isinstance(query, str):
        return build_hybrid_retriever(query, semantic_weight, k, rrf_k).invoke(sparse_weight)

    semantic_docs = semantic_search(query, k)

    bm25 = get_bm25_index(k)

    bm25_docs = bm25.invoke(query)

    return reciprocal_rank_fusion(semantic_docs, bm25_docs, rrf_k=rrf_k)
