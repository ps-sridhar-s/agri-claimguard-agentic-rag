from pathlib import Path

from src.knowledge_base import KnowledgeBase
from langchain_classic.schema import Document


def test_discover_files_empty(tmp_path):
    kb = KnowledgeBase(source_dir=tmp_path)
    assert kb.discover_files() == []


def test_load_documents_text_file(tmp_path):
    sample_text = tmp_path / "policy.txt"
    sample_text.write_text("policy coverage for drought claims", encoding="utf-8")

    kb = KnowledgeBase(source_dir=tmp_path)
    docs = kb.load_documents([sample_text])

    assert len(docs) == 1
    assert docs[0].page_content == "policy coverage for drought claims"
    assert docs[0].metadata["source"] == str(sample_text)


def test_build_without_embeddings_uses_bm25(tmp_path, monkeypatch):
    sample_text = tmp_path / "policy.txt"
    sample_text.write_text("policy coverage for drought claims", encoding="utf-8")

    monkeypatch.setenv("AGRICLAIMGUARD_ENABLE_VECTOR", "false")

    kb = KnowledgeBase(source_dir=tmp_path, persist_dir=tmp_path / "db")
    kb.build()

    assert kb.bm25_enabled is True
    assert kb.vector_store_enabled is False
    assert kb.retriever is not None

    results = kb.retrieve("drought")
    assert len(results) >= 1
    assert "drought" in results[0].page_content
