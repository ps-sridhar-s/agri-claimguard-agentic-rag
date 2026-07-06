from langchain_chroma import Chroma
from langchain_classic.retrievers import BM25Retriever, EnsembleRetriever
from models.embeddings_models import embedding_client




def chunk_vector_store(chunks):
    vectorstore = Chroma(
        collection_name="crop_insurance",
        persist_directory="./chroma_db",
        embedding_function=embedding_client
    )
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    return vectorstore


