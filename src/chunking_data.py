from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_classic.schema import Document


def chunk_documents(documents, chunk_size=1000, chunk_overlap=300):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)


