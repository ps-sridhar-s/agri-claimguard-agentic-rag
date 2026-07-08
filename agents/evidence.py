from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from agents.mcp_tools import collect_evidence
from models.chatting_model import get_chat_client

load_dotenv()

model = get_chat_client()

evidence_agent = create_react_agent(
    model=model,
    tools=[collect_evidence],
    prompt="""
You are the Evidence Agent.

Organize evidence from specialist agents into claim, policy, weather,
and historical sections. Identify missing, conflicting, or duplicate evidence.
Never invent evidence and never make recommendations.
""",
    name="evidence_agent",
)
