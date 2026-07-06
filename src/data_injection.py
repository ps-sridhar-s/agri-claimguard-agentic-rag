from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path
def document_loader(file_path):
    loader = PyMuPDFLoader(str(file_path))
    docs = loader.load()
    return docs


