from __future__ import annotations

from src.schemas import EvalResult


def to_ragas_rows(results: list[EvalResult]) -> list[dict]:
    """Export eval results in a shape compatible with RAGAS datasets.

    RAGAS itself is intentionally optional for this prototype. Install and run
    RAGAS separately if you want model-based faithfulness/context metrics.
    """
    rows = []
    for result in results:
        rows.append(
            {
                "question": result.query,
                "answer": result.assessment.answer,
                "contexts": [
                    citation.snippet for citation in result.assessment.citations
                ],
                "ground_truth": (
                    result.assessment.recommendation.value
                    if result.assessment.recommendation
                    else ""
                ),
                "case_id": result.case_id,
            }
        )
    return rows


def ragas_status() -> dict:
    try:
        import ragas  # type: ignore

        return {
            "available": True,
            "version": getattr(ragas, "__version__", "unknown"),
            "message": "RAGAS is installed and can be used with to_ragas_rows().",
        }
    except Exception:
        return {
            "available": False,
            "version": None,
            "message": "RAGAS is optional and is not installed in this environment.",
        }
