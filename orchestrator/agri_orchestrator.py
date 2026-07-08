

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

# Replace these imports with your implementations
from agents.claim import claim_agent
from agents.policy import policy_agent
from agents.weather import weather_agent
from agents.historical_claim import historical_claim_agent
from agents.evidence import evidence_agent
from agents.reasoning import reasoning_agent


class AgriState(TypedDict):
    claim: dict
    policy_response: str
    weather_response: str
    historical_response: str
    evidence_response: str
    reasoning_response: str


def pause(node_name: str):
    interrupt({
        "completed_node": node_name,
        "message": f"{node_name} completed. Resume to continue."
    })


def claim_node(state: AgriState):
    r = claim_agent.invoke({"messages":[("user", str(state["claim"]))]})
    state["claim"] = r["messages"][-1].content
    pause("Claim Agent")
    return state


def policy_node(state: AgriState):
    r = policy_agent.invoke({"messages":[("user", state["claim"])]})
    state["policy_response"] = r["messages"][-1].content
    pause("Policy Agent")
    return state


def weather_node(state: AgriState):
    r = weather_agent.invoke({"messages":[("user", state["claim"])]})
    state["weather_response"] = r["messages"][-1].content
    pause("Weather Agent")
    return state


def historical_node(state: AgriState):
    r = historical_claim_agent.invoke({"messages":[("user", state["claim"])]})
    state["historical_response"] = r["messages"][-1].content
    pause("Historical Agent")
    return state


def evidence_node(state: AgriState):
    prompt = f"""
Claim:
{state['claim']}

Policy:
{state['policy_response']}

Weather:
{state['weather_response']}

Historical:
{state['historical_response']}
"""
    r = evidence_agent.invoke({"messages":[("user", prompt)]})
    state["evidence_response"] = r["messages"][-1].content
    pause("Evidence Agent")
    return state


def reasoning_node(state: AgriState):
    prompt = f"""
Claim:
{state['claim']}

Policy:
{state['policy_response']}

Weather:
{state['weather_response']}

Historical:
{state['historical_response']}

Evidence:
{state['evidence_response']}
"""
    r = reasoning_agent.invoke({"messages":[("user", prompt)]})
    state["reasoning_response"] = r["messages"][-1].content
    pause("Reasoning Agent")
    return state


builder = StateGraph(AgriState)

builder.add_node("claim", claim_node)
builder.add_node("policy", policy_node)
builder.add_node("weather", weather_node)
builder.add_node("historical", historical_node)
builder.add_node("evidence", evidence_node)
builder.add_node("reasoning", reasoning_node)

builder.add_edge(START, "claim")

# Build a strictly sequential workflow so only one interrupt is pending at a time.
builder.add_edge("claim", "policy")
builder.add_edge("policy", "weather")
builder.add_edge("weather", "historical")
builder.add_edge("historical", "evidence")

builder.add_edge("evidence", "reasoning")
builder.add_edge("reasoning", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "claim-demo"
        }
    }

    initial_state = {
        "claim": {
            "farmer_name": "Ramesh",
            "policy_id": "POL123",
            "crop": "Rice",
            "district": "Hyderabad",
            "loss_reason": "Heavy Rain",
            "loss_date": "2025-06-15",
        }
    }

    result = graph.invoke(initial_state, config=config)
    print(result)

    while True:
        cmd = input("\nType 'resume' to continue or 'exit': ").strip().lower()

        if cmd == "exit":
            break

        if cmd == "resume":
            result = graph.invoke(Command(resume=True), config=config)
            print(result)
