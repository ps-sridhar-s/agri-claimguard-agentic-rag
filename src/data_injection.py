from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path
def document_loader(file_path):
    loader = PyMuPDFLoader(str(file_path))
    docs = loader.load()
    return docs


# if __name__ == "__main__":
#     document = document_loader(file_path=Path("C:/Users/SridharS/Downloads/Sridhar_Project/agri-claimguard-agentic-rag/data_source/NAIS_SCHEME.pdf"))
#     print(document)