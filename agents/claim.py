from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from agents.mcp_tools import (
    check_policy,
    normalize_crop,
    normalize_location,
    validate_claim,
)
from models.chatting_model import get_chat_client

load_dotenv()

model = get_chat_client()

claim_agent = create_react_agent(
    model=model,
    tools=[
        validate_claim,
        normalize_crop,
        normalize_location,
        check_policy,
    ],
    prompt="""
You are a Crop Insurance Claim Agent.

Responsibilities:
1. Read the user's claim.
2. Extract important information.
3. Normalize crop names and district names.
4. Verify policy status using the tool.
5. Validate mandatory fields.
6. Never approve or reject the claim.
7. Return only structured claim information.
""",
    name="claim_agent",
)
