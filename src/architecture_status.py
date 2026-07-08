from __future__ import annotations


def architecture_status() -> dict:
    return {
        "data_sources": {
            "insurance_policies": "implemented via PDF/DOCX/TXT/CSV ingestion",
            "government_regulations": "implemented when documents are placed in data_source",
            "historical_claims": "partial; retrieved if uploaded as CSV/PDF/TXT",
            "weather_data": "implemented as optional OpenWeather integration; requires OPENWEATHER_API_KEY",
            "farmer_submissions": "implemented through API/UI claim request",
        },
        "agentic_orchestration_layer": {
            "supervisor_agent": "implemented",
            "policy_agent": "implemented with LangGraph create_react_agent",
            "weather_agent": "implemented with LangGraph create_react_agent and optional live API",
            "claim_agent": "implemented as Historical Claim Agent with LangGraph create_react_agent",
            "evidence_agent": "implemented with LangGraph create_react_agent",
            "reasoning_agent": "implemented with LangGraph create_react_agent and optional NVIDIA LLM",
            "compliance_agent": "implemented with LangGraph create_react_agent",
            "memory": "partial; audit/session logs stored locally, Redis can be added in deployment",
            "planning_and_routing": "implemented by Supervisor Agent plan",
            "reflection_self_correction": "partial; compliance flags missing evidence for human review",
        },
        "rag_retrieval_layer": {
            "document_ingestion": "implemented",
            "data_processing": "implemented",
            "embeddings": "implemented with NVIDIA embeddings when env vars are set",
            "vector_store": "implemented with Chroma; Qdrant is an architecture target",
            "hybrid_retrieval": "implemented with Chroma + BM25 ensemble, BM25 fallback",
            "reranking": "not implemented; planned extension",
            "context_compression": "basic top-k evidence selection implemented",
            "llm_generation": "implemented with NVIDIA chat model when env vars are set, deterministic fallback otherwise",
        },
        "output_user_experience": {
            "claim_recommendation": "implemented",
            "confidence_score": "implemented",
            "evidence_citations": "implemented",
            "human_in_the_loop": "implemented as Needs Review flag and review reasons",
            "audit_trail": "implemented in storage/audit_logs",
        },
        "security_governance": {
            "authentication_rbac": "not implemented in free prototype",
            "encryption": "handled by hosting platform TLS for deployed app",
            "pii_masking": "partial; avoid submitting sensitive production data",
            "audit_logs": "implemented",
            "rate_limiting": "not implemented in free prototype",
            "compliance_checks": "implemented as Compliance Agent",
        },
        "platform_infrastructure": {
            "fastapi": "implemented",
            "docker": "deployment files can be added if needed",
            "redis": "optional future memory backend",
            "qdrant": "architecture target; Chroma used in prototype",
            "postgresql": "not needed for free prototype",
            "object_storage": "not needed for free prototype",
            "nginx": "provided by hosting platform",
        },
        "observability_evaluation_ops": {
            "langsmith": "dependency present; configure env vars to enable",
            "phoenix": "not implemented",
            "ragas_deepeval": "partial; deterministic eval suite and RAGAS export adapter implemented",
            "eval_api": "implemented at /eval/status and /eval/run",
            "eval_cli": "implemented with python -m evals.run_evals",
            "prometheus_grafana": "not implemented in free prototype",
            "github_actions": "not implemented",
        },
    }
