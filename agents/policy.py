from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from agents.mcp_tools import hybrid_search_tool
from models.chatting_model import get_chat_client

load_dotenv()

model = get_chat_client()

policy_agent = create_react_agent(
    model=model,
    tools=[hybrid_search_tool],
    prompt="""
You are a policy agent for agricultural policies and regulations.

Use the hybrid search tool when the answer needs policy evidence.
Return a concise answer based on retrieved information.
Never invent policy details.
""",
    name="policy_agent",
)
