from langchain_classic.schema import Document

from src.chunking_data import chunk_documents


def test_chunk_documents_splits_long_text():
    long_text = " ".join(str(i) for i in range(0, 1500))
    document = Document(page_content=long_text, metadata={"source": "long_doc"})
    chunks = chunk_documents([document], chunk_size=200, chunk_overlap=50)

    assert len(chunks) > 1
    assert all(hasattr(chunk, "page_content") for chunk in chunks)
    reconstructed = "".join(chunk.page_content for chunk in chunks)
    assert "0" in reconstructed
    assert "1499" in reconstructed
