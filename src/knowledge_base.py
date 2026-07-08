from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from langchain_classic.schema import Document
from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)
from langchain_community.retrievers import BM25Retriever
from langchain_core.retrievers import BaseRetriever

from src.chunking_data import chunk_documents
from src.retrieval import build_hybrid_retriever
from src.vector_storage import create_vector_store

load_dotenv()

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv", ".docx"}


class KnowledgeBase:
    def __init__(
        self,
        source_dir: str | Path | None = None,
        persist_dir: str | Path = "chroma_db",
        collection_name: str = "crop_insurance",
    ):
        self.source_dir = Path(
            source_dir or os.environ.get("folder_path") or "data_source"
        )
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.documents: list[Document] = []
        self.chunks: list[Document] = []
        self.vector_store = None
        self.bm25_index: BM25Retriever | None = None
        self.retriever: BaseRetriever | BM25Retriever | None = None
        self.vector_store_enabled = False
        self.bm25_enabled = False

    def discover_files(self) -> list[Path]:
        if not self.source_dir.exists():
            return []

        files: list[Path] = []
        for file in self.source_dir.rglob("*"):
            if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(file)
        return sorted(files)

    def load_documents(self, files: Iterable[Path]) -> list[Document]:
        documents: list[Document] = []
        for file in files:
            loader = self._loader_for(file)
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = str(file)
            documents.extend(docs)
        return documents

    def build(self, force_rebuild: bool = False) -> "KnowledgeBase":
        files = self.discover_files()
        self.documents = self.load_documents(files)
        self.chunks = chunk_documents(self.documents) if self.documents else []

        if not self.chunks:
            self.bm25_index = None
            self.retriever = None
            self.vector_store = None
            return self

        self.bm25_index = BM25Retriever.from_documents(self.chunks)
        self.bm25_index.k = 5
        self.bm25_enabled = True

        if not self._embeddings_configured():
            self.vector_store_enabled = False
            self.retriever = self.bm25_index
            return self

        try:
            self.vector_store = create_vector_store(
                self.chunks,
                collection_name=self.collection_name,
                persist_directory=str(self.persist_dir),
                force_rebuild=force_rebuild,
            )
            self.vector_store_enabled = True
            self.retriever = build_hybrid_retriever(self.vector_store, self.bm25_index)
        except Exception as exc:
            self.vector_store_enabled = False
            self.retriever = self.bm25_index
            print(f"Vector store unavailable, falling back to BM25 only: {exc}")

        return self

    def retrieve(self, query: str, k: int = 5) -> list[Document]:
        if self.retriever is None:
            self.build()
        if self.retriever is None:
            return []

        docs = self.retriever.invoke(query)
        return docs[:k]

    def status(self) -> dict:
        return {
            "source_dir": str(self.source_dir),
            "supported_files": len(self.discover_files()),
            "documents": len(self.documents),
            "chunks": len(self.chunks),
            "vector_store_enabled": self.vector_store_enabled,
            "bm25_enabled": self.bm25_enabled,
        }

    @staticmethod
    def _loader_for(file: Path):
        suffix = file.suffix.lower()
        if suffix == ".pdf":
            return PyMuPDFLoader(str(file))
        if suffix == ".docx":
            return Docx2txtLoader(str(file))
        if suffix == ".csv":
            return CSVLoader(str(file))
        return TextLoader(str(file), encoding="utf-8")

    @staticmethod
    def _embeddings_configured() -> bool:
        if os.environ.get("AGRICLAIMGUARD_ENABLE_VECTOR", "").lower() != "true":
            return False
        return bool(
            os.environ.get("nvidia_embedding_key")
            and os.environ.get("nvidia_embedding_model")
        )


_kb: KnowledgeBase | None = None


def get_knowledge_base(force_rebuild: bool = False) -> KnowledgeBase:
    global _kb
    if _kb is None or force_rebuild:
        _kb = KnowledgeBase().build(force_rebuild=force_rebuild)
    return _kb
