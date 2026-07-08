from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from agents.mcp_tools import get_weather
from models.chatting_model import get_chat_client

load_dotenv()

model = get_chat_client()

weather_agent = create_react_agent(
    model=model,
    tools=[get_weather],
    prompt="""
You are a Weather Agent.

Always use the weather tool for weather questions.
Summarize the returned weather naturally.
Do not make up weather information.
""",
    name="weather_agent",
)
