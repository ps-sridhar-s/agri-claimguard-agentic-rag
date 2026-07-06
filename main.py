from src.safe_file_renamer import rename_files
from src.data_injection import document_loader
from src.chunking_data import chunk_documents
from src.vector_storage import chunk_vector_store
from src.bm25_index import create_bm25_index
from src.retrieval import hybrid_retriever
from pathlib import Path
from langchain_classic.schema import Document
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever



class Rag_State(TypedDict, total=False):
    query: str

    documents_paths: List[Path]
    documents: List[Document]
    chunks: List[Document]

    vector_store: Chroma
    bm25_index: BM25Retriever

    retriever: object


def log_node(name: str, state):
    print("\n" + "=" * 80)
    print(f"NODE: {name}")
    print("State Keys:", list(state.keys()))
    print("=" * 80)


rag_graph = StateGraph(Rag_State)

def document_path_returning_node(state: Rag_State):
    file_paths=rename_files()
    print(file_paths)
    return {"documents_paths": file_paths}

def document_loading_node(state: Rag_State):
    file_paths=state["documents_paths"]
    documents=[]
    for file_path in file_paths:
        docs=document_loader(file_path)
        documents.extend(docs)  
    return {"documents": documents}

def chunking_node(state: Rag_State):
    documents = state["documents"]

    print(type(documents))
    print(len(documents))
    

    splitted_chunks = chunk_documents(documents)

    return {"chunks": splitted_chunks}


def vector_store_node(state: Rag_State):
    chunks=state["chunks"]
    log_node("vector_store_node", state)
    vector_store=chunk_vector_store(chunks)
    return {"vector_store": vector_store}




def bm25_index_node(state: Rag_State):
    chunks=state["chunks"]
    bm25_index=create_bm25_index(chunks)
    return {"bm25_index": bm25_index}


def hybrid_retriever_node(state: Rag_State):
    vector_store=state["vector_store"]
    bm25_index=state["bm25_index"]
    results=hybrid_retriever(vector_store,bm25_index,state["query"])
    return {"retriever": results}



def text_generation_node(state: Rag_State):
    retriever=state["retriever"]
    return retriever.invoke(state["query"])



rag_graph.add_node(
    "document_path_returning",
    document_path_returning_node,
)

rag_graph.add_node(
    "document_loading",
    document_loading_node,
)

rag_graph.add_node(
    "chunking",
    chunking_node,
)

rag_graph.add_node(
    "vector_store",
    vector_store_node,
)

rag_graph.add_node(
    "bm25_index",
    bm25_index_node,
)

rag_graph.add_node(
    "hybrid_retriever",
    hybrid_retriever_node,
)

rag_graph.add_edge(
    START,
    "document_path_returning"
)

rag_graph.add_edge(
    "document_path_returning",
    "document_loading"
)

rag_graph.add_edge(
    "document_loading",
    "chunking"
)

rag_graph.add_edge(
    "chunking",
    "vector_store"
)

rag_graph.add_edge(
    "chunking",
    "bm25_index"
)

rag_graph.add_edge(
    "vector_store",
    "hybrid_retriever"
)

rag_graph.add_edge(
    "bm25_index",
    "hybrid_retriever"
)

rag_graph.add_edge(
    "hybrid_retriever",
    END
)




if __name__=="__main__":
    workflow = rag_graph.compile()

    initial_state = {
        "query": "What is the eligibility for drought compensation?"
    }
    with open("assets/ingestion_graph.png", "wb") as f:
        f.write(workflow.get_graph().draw_mermaid_png())

    result = workflow.invoke(initial_state)

    print(result)
