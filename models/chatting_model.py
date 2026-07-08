import os
from xml.parsers.expat import model

from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama


load_dotenv()


def get_chat_client():
    from langchain_ollama import ChatOllama
    model = ChatOllama(
    model="llama3.1:8b")
    return model

# def get_chat_client():
#     model = os.environ.get("nvidia_chat_model")
#     api_key = os.environ.get("nvidia_chat_key")
#     if not model or not api_key:
#         raise RuntimeError(
#             "Missing nvidia_chat_model or nvidia_chat_key environment variable."
#         )

#     chat_client = ChatNVIDIA(
#         model=model,
#         nvidia_api_key=api_key,
#         temperature=0.2,
#         top_p=0.9    )
#     return chat_client

