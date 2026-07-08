from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from agents.mcp_tools import validate_compliance
from models.chatting_model import get_chat_client

load_dotenv()

model = get_chat_client()

compliance_agent = create_react_agent(
    model=model,
    tools=[validate_compliance],
    prompt="""
You are the Compliance Agent.

Review the reasoning and evidence outputs. Check mandatory fields, policy
evidence, weather verification, conflicting evidence, and confidence.
Return PASS or FAIL and say whether the decision can be released or needs human review.
""",
    name="compliance_agent",
)
