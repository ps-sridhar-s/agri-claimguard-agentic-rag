# pip install -qU langchain "langchain[anthropic]"
from langchain.agents import create_agent
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()
from models.chatting_model import chat_client

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"






Policy_Agent = create_agent(
    model=chat_client,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

