
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os
chat_client = ChatNVIDIA(
  model=os.environ["nvidia_chat_model"],
  api_key=os.environ["nvidia_chat_key"], 
  temperature=1,
  top_p=0.95,
  max_tokens=16384,
  chat_template_kwargs={"enable_thinking":True},
)