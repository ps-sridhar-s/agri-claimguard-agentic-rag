from __future__ import annotations

import os

from models.chatting_model import get_chat_client
from src.schemas import ClaimAssessment, EvalMetric


def llm_faithfulness_judge(assessment: ClaimAssessment) -> EvalMetric:
    """Optional LLM judge for answer faithfulness against citations.

    This is disabled by default so free deployments remain fast and stable.
    Set AGRICLAIMGUARD_ENABLE_LLM_JUDGE=true to enable it.
    """
    if os.environ.get("AGRICLAIMGUARD_ENABLE_LLM_JUDGE", "").lower() != "true":
        return EvalMetric(
            name="llm_faithfulness_judge",
            score=1.0,
            passed=True,
            details="Skipped; set AGRICLAIMGUARD_ENABLE_LLM_JUDGE=true to enable.",
        )

    evidence = "\n".join(
        f"- {citation.source} page {citation.page}: {citation.snippet}"
        for citation in assessment.citations
    )
    prompt = (
        "You are an evaluator. Score whether the answer is supported by the citations. "
        "Return only a number from 0 to 1.\n\n"
        f"Answer:\n{assessment.answer}\n\nCitations:\n{evidence}"
    )
    try:
        response = get_chat_client().invoke(prompt)
        content = getattr(response, "content", response)
        text = str(content).strip()
        score = float(text.split()[0])
        score = max(0.0, min(1.0, score))
        return EvalMetric(
            name="llm_faithfulness_judge",
            score=score,
            passed=score >= 0.75,
            details=f"LLM judge score: {score:.2f}.",
        )
    except Exception as exc:
        return EvalMetric(
            name="llm_faithfulness_judge",
            score=0.0,
            passed=False,
            details=f"LLM judge failed: {exc}",
        )
