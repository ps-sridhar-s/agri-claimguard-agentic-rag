from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from agents.mcp_tools import historical_statistics, search_historical_claims
from models.chatting_model import get_chat_client

load_dotenv()

model = get_chat_client()

historical_claim_agent = create_react_agent(
    model=model,
    tools=[
        search_historical_claims,
        historical_statistics,
    ],
    prompt="""
You are an Agricultural Historical Claim Agent.

Always use the available tools to retrieve similar historical claims.
Compare crop, district, and loss reason.
Summarize similar claims, approval rate, and average payout.
Do not approve, reject, predict payout, or make recommendations.
""",
    name="historical_claim_agent",
)
