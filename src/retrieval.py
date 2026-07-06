
from langchain_classic.retrievers import BM25Retriever, EnsembleRetriever
from models.embeddings_models import embedding_client




def hybrid_retriever(vectorstore,bm_25,user_query):
    

    semantic = vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )

    hybrid = EnsembleRetriever(
        retrievers=[semantic, bm_25],
        weights=[0.7, 0.3]
    )
    results = hybrid.invoke(user_query
    
)

    return results





