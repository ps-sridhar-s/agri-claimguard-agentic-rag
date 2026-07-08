import importlib
import sys

from langchain_core.documents import Document


class FakeAgent:
    def __init__(self, model, tools, prompt):
        self.model = model
        self.tools = tools
        self.prompt = prompt

    def invoke(self, payload):
        return {
            "messages": [
                type("Message", (), {"content": "policy response"})(),
            ]
        }


def import_policy_module(monkeypatch):
    captured = {}
    fake_model = object()

    def fake_create_react_agent(model, tools, prompt, **kwargs):
        captured["model"] = model
        captured["tools"] = tools
        captured["prompt"] = prompt
        captured["kwargs"] = kwargs
        return FakeAgent(model, tools, prompt)

    monkeypatch.setattr("models.chatting_model.get_chat_client", lambda: fake_model)
    monkeypatch.setattr("langgraph.prebuilt.create_react_agent", fake_create_react_agent)

    sys.modules.pop("agents.policy", None)
    policy = importlib.import_module("agents.policy")

    return policy, captured, fake_model


def test_policy_agent_is_created_on_import(monkeypatch):
    policy, captured, fake_model = import_policy_module(monkeypatch)

    assert isinstance(policy.policy_agent, FakeAgent)
    assert captured["model"] is fake_model


def test_policy_agent_registers_hybrid_search_tool(monkeypatch):
    policy, captured, _ = import_policy_module(monkeypatch)

    assert captured["tools"] == [policy.hybrid_search_tool]


def test_policy_agent_prompt_mentions_policy_responsibility(monkeypatch):
    _, captured, _ = import_policy_module(monkeypatch)

    assert "policy agent" in captured["prompt"].lower()
    assert "agricultural policies and regulations" in captured["prompt"].lower()


def test_policy_agent_prompt_instructs_tool_usage(monkeypatch):
    _, captured, _ = import_policy_module(monkeypatch)

    prompt = captured["prompt"].lower()

    assert "hybrid search tool" in prompt
    assert "retrieved information" in prompt


def test_hybrid_search_tool_delegates_to_retriever(monkeypatch):
    policy, _, _ = import_policy_module(monkeypatch)
    mcp_tools = importlib.import_module("agents.mcp_tools")
    calls = []

    def fake_hybrid_search(query):
        calls.append(query)
        return [Document(page_content="drought eligibility", metadata={"source": "policy"})]

    monkeypatch.setattr(mcp_tools, "hybrid_retriever", fake_hybrid_search)

    result = policy.hybrid_search_tool.invoke(
        {"query": "What is the eligibility for drought compensation?"}
    )

    assert calls == ["What is the eligibility for drought compensation?"]
    assert result[0].page_content == "drought eligibility"


def test_hybrid_search_tool_preserves_document_metadata(monkeypatch):
    policy, _, _ = import_policy_module(monkeypatch)
    mcp_tools = importlib.import_module("agents.mcp_tools")
    expected = [
        Document(
            page_content="Policy covers notified drought in insured areas.",
            metadata={"source": "pmfby-guidelines", "page": 3},
        )
    ]

    monkeypatch.setattr(mcp_tools, "hybrid_retriever", lambda query: expected)

    result = policy.hybrid_search_tool.invoke({"query": "drought coverage"})

    assert result[0].metadata == {"source": "pmfby-guidelines", "page": 3}


def test_hybrid_search_tool_returns_empty_results(monkeypatch):
    policy, _, _ = import_policy_module(monkeypatch)
    mcp_tools = importlib.import_module("agents.mcp_tools")

    monkeypatch.setattr(mcp_tools, "hybrid_retriever", lambda query: [])

    assert policy.hybrid_search_tool.invoke({"query": "unknown policy"}) == []


def test_policy_agent_fake_invoke_returns_last_message(monkeypatch):
    policy, _, _ = import_policy_module(monkeypatch)

    result = policy.policy_agent.invoke({"messages": [("user", "check policy")]})

    assert result["messages"][-1].content == "policy response"
