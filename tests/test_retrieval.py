from src import retrieval
from src.retrieval import build_hybrid_retriever, hybrid_retriever, reciprocal_rank_fusion
from langchain_core.retrievers import BaseRetriever
from langchain_classic.schema import Document


class FakeRetriever(BaseRetriever):
    docs: list[Document]

    def _get_relevant_documents(self, query: str):
        return self.docs


class FakeVectorStore:
    def __init__(self, docs):
        self.docs = docs

    def as_retriever(self, search_kwargs=None):
        return FakeRetriever(docs=self.docs)


def test_build_hybrid_retriever_combines_retrievers():
    semantic_docs = [Document(page_content="policy evidence", metadata={"source": "semantic"})]
    sparse_docs = [Document(page_content="policy text", metadata={"source": "sparse"})]
    vectorstore = FakeVectorStore(semantic_docs)
    bm25 = FakeRetriever(docs=sparse_docs)

    hybrid = build_hybrid_retriever(vectorstore, bm25)
    results = hybrid.invoke("policy")

    assert isinstance(results, list)
    assert any(doc.metadata["source"] == "semantic" for doc in results)
    assert any(doc.metadata["source"] == "sparse" for doc in results)


def test_hybrid_retriever_returns_results():
    semantic_docs = [Document(page_content="climate evidence", metadata={"source": "semantic"})]
    sparse_docs = [Document(page_content="farm rules", metadata={"source": "sparse"})]
    vectorstore = FakeVectorStore(semantic_docs)
    bm25 = FakeRetriever(docs=sparse_docs)

    results = hybrid_retriever(vectorstore, bm25, "weather")

    assert isinstance(results, list)
    assert len(results) >= 2
    assert {doc.page_content for doc in results} == {"climate evidence", "farm rules"}


def test_reciprocal_rank_fusion_promotes_documents_seen_in_multiple_rankers():
    semantic_docs = [
        Document(page_content="semantic only top", metadata={"source": "semantic"}),
        Document(page_content="shared policy", metadata={"source": "policy"}),
    ]
    bm25_docs = [
        Document(page_content="bm25 only top", metadata={"source": "bm25"}),
        Document(page_content="shared policy", metadata={"source": "policy"}),
    ]

    results = reciprocal_rank_fusion(semantic_docs, bm25_docs, rrf_k=60)

    assert results[0].page_content == "shared policy"
    assert [doc.page_content for doc in results].count("shared policy") == 1


def test_reciprocal_rank_fusion_preserves_best_document_metadata():
    semantic_doc = Document(
        page_content="shared policy",
        metadata={"source": "policy", "ranker": "semantic"},
    )
    bm25_doc = Document(
        page_content="shared policy",
        metadata={"source": "policy", "ranker": "bm25"},
    )

    results = reciprocal_rank_fusion([semantic_doc], [bm25_doc], rrf_k=60)

    assert len(results) == 1
    assert results[0].metadata["ranker"] == "semantic"


class FakeMilvusClient:
    def __init__(self):
        self.loaded_collections = []
        self.search_collection = None

    def load_collection(self, collection_name):
        self.loaded_collections.append(collection_name)

    def get_load_state(self, collection_name):
        return {"state": "Loaded"}

    def search(self, collection_name, data, limit, output_fields):
        self.search_collection = collection_name
        assert self.loaded_collections[-1] == collection_name
        return [[{"entity": {"text": "loaded policy", "metadata": {"source": "milvus"}}}]]


class FakeEmbeddingClient:
    def embed_query(self, query):
        return [0.1, 0.2, 0.3]


def test_semantic_search_loads_collection_before_search(monkeypatch):
    fake_client = FakeMilvusClient()
    monkeypatch.setattr(retrieval, "get_vectorstore", lambda: fake_client)
    monkeypatch.setattr(retrieval, "embedding_client", FakeEmbeddingClient())

    results = retrieval.semantic_search("drought compensation", collection_name="crop_insurance")

    assert fake_client.loaded_collections == ["crop_insurance"]
    assert fake_client.search_collection == "crop_insurance"
    assert results[0].page_content == "loaded policy"


class ReleasedOnceMilvusClient(FakeMilvusClient):
    def __init__(self):
        super().__init__()
        self.search_calls = 0

    def search(self, collection_name, data, limit, output_fields):
        self.search_calls += 1

        if self.search_calls == 1:
            raise Exception(
                "Collection 'crop_insurance' is in state 'released'; "
                "call load() before search/get/query"
            )

        return super().search(collection_name, data, limit, output_fields)


def test_semantic_search_reloads_and_retries_released_collection(monkeypatch):
    fake_client = ReleasedOnceMilvusClient()
    monkeypatch.setattr(retrieval, "get_vectorstore", lambda: fake_client)
    monkeypatch.setattr(retrieval, "embedding_client", FakeEmbeddingClient())

    results = retrieval.semantic_search("drought compensation", collection_name="crop_insurance")

    assert fake_client.loaded_collections == ["crop_insurance", "crop_insurance"]
    assert fake_client.search_calls == 2
    assert results[0].page_content == "loaded policy"
