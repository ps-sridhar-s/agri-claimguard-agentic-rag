from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from agents.mcp_tools import inspect_claim_information
from models.chatting_model import get_chat_client

load_dotenv()

model = get_chat_client()

reasoning_agent = create_react_agent(
    model=model,
    tools=[inspect_claim_information],
    prompt="""
You are an Insurance Claim Reasoning Agent.

Analyze the claim, policy, weather, historical, and evidence outputs.
Explain reasoning step by step, include confidence from 0 to 100,
and recommend Eligible, Not Eligible, or Needs Human Review.
Never invent facts.
""",
    name="reasoning_agent",
)
