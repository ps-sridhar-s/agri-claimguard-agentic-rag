from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()




def get_embedding_client():
    embedding_client =  OllamaEmbeddings(
    model="mxbai-embed-large",
    base_url="http://localhost:11434")
    
    return embedding_client





embedding_client = get_embedding_client()




