from langchain_classic.schema import Document

from src.bm25_index import create_bm25_index


def test_create_bm25_index_retrieves_relevant_documents():
    docs = [
        Document(page_content="apple banana cherry", metadata={"source": "doc1"}),
        Document(page_content="banana citrus date", metadata={"source": "doc2"}),
        Document(page_content="elephant fig grape", metadata={"source": "doc3"}),
    ]

    bm25 = create_bm25_index(docs, k=2)
    results = bm25.invoke("banana")

    assert len(results) > 0
    assert any("banana" in result.page_content for result in results)
