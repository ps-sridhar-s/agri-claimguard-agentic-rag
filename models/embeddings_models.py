from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
embedding_client = NVIDIAEmbeddings(
  model=os.environ.get("nvidia_embedding_model"), 
  api_key=os.environ.get("nvidia_embedding_key"), 
  truncate="NONE", 
  )


