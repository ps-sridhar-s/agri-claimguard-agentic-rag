from __future__ import annotations

import re
import time
from collections import defaultdict

from agents.claim_workflow import ClaimAssessmentService
from evals.llm_as_judge import llm_faithfulness_judge
from src.schemas import (
    ClaimAssessment,
    EvalCase,
    EvalMetric,
    EvalResult,
    EvalSuiteReport,
)


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "with",
    "this", "will", "can", "if", "when", "then", "than", "into", "over",
}


def normalize_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return {token for token in tokens if token not in STOPWORDS}


def evaluate_assessment(
    case: EvalCase,
    assessment: ClaimAssessment,
    latency_ms: float,
    pass_threshold: float = 0.65,
) -> EvalResult:
    metrics = [
        citation_coverage(assessment),
        groundedness(assessment),
        keyword_coverage(case, assessment),
        recommendation_match(case, assessment),
        source_recall(case, assessment),
        human_review_match(case, assessment),
        agent_completion(assessment),
        latency_score(latency_ms),
        llm_faithfulness_judge(assessment),
    ]
    overall = sum(metric.score for metric in metrics) / len(metrics)
    return EvalResult(
        case_id=case.id,
        query=assessment.query,
        recommendation=assessment.recommendation,
        confidence=assessment.confidence,
        latency_ms=latency_ms,
        metrics=metrics,
        overall_score=overall,
        passed=overall >= pass_threshold,
        assessment=assessment,
    )


def run_eval_suite(
    cases: list[EvalCase],
    service: ClaimAssessmentService,
    pass_threshold: float = 0.65,
) -> EvalSuiteReport:
    results: list[EvalResult] = []
    for case in cases:
        started = time.perf_counter()
        assessment = service.assess(case.claim)
        latency_ms = (time.perf_counter() - started) * 1000
        results.append(evaluate_assessment(case, assessment, latency_ms, pass_threshold))

    metrics_accumulator: dict[str, list[float]] = defaultdict(list)
    for result in results:
        for metric in result.metrics:
            metrics_accumulator[metric.name].append(metric.score)

    summary = {
        name: sum(scores) / len(scores)
        for name, scores in metrics_accumulator.items()
    }
    average_score = (
        sum(result.overall_score for result in results) / len(results)
        if results
        else 0.0
    )
    return EvalSuiteReport(
        total_cases=len(results),
        passed_cases=sum(1 for result in results if result.passed),
        average_score=average_score,
        metrics_summary=summary,
        results=results,
    )


def citation_coverage(assessment: ClaimAssessment) -> EvalMetric:
    count = len(assessment.citations)
    score = 1.0 if count > 0 else 0.0
    return EvalMetric(
        name="citation_coverage",
        score=score,
        passed=score == 1.0,
        details=f"{count} citations returned.",
    )


def groundedness(assessment: ClaimAssessment) -> EvalMetric:
    answer_tokens = normalize_tokens(assessment.answer)
    citation_tokens = normalize_tokens(
        " ".join(citation.snippet for citation in assessment.citations)
    )
    if not answer_tokens:
        score = 0.0
    elif not citation_tokens:
        score = 0.0
    else:
        score = len(answer_tokens & citation_tokens) / max(1, len(answer_tokens))
    score = min(1.0, score * 2.0)
    return EvalMetric(
        name="groundedness_overlap",
        score=score,
        passed=score >= 0.45,
        details="Token overlap between answer and citation snippets.",
    )


def keyword_coverage(case: EvalCase, assessment: ClaimAssessment) -> EvalMetric:
    if not case.expected_keywords:
        return EvalMetric(
            name="keyword_coverage",
            score=1.0,
            passed=True,
            details="No expected keywords configured.",
        )
    evidence_text = " ".join(
        [assessment.answer] + [citation.snippet for citation in assessment.citations]
    ).lower()
    hits = [
        keyword
        for keyword in case.expected_keywords
        if keyword.lower() in evidence_text
    ]
    score = len(hits) / len(case.expected_keywords)
    return EvalMetric(
        name="keyword_coverage",
        score=score,
        passed=score >= 0.6,
        details=f"Matched {len(hits)}/{len(case.expected_keywords)} keywords: {hits}.",
    )


def recommendation_match(case: EvalCase, assessment: ClaimAssessment) -> EvalMetric:
    if case.expected_recommendation is None:
        return EvalMetric(
            name="recommendation_match",
            score=1.0,
            passed=True,
            details="No expected recommendation configured.",
        )
    score = 1.0 if assessment.recommendation == case.expected_recommendation else 0.0
    return EvalMetric(
        name="recommendation_match",
        score=score,
        passed=score == 1.0,
        details=(
            f"Expected {case.expected_recommendation.value}, "
            f"got {assessment.recommendation.value}."
        ),
    )


def source_recall(case: EvalCase, assessment: ClaimAssessment) -> EvalMetric:
    if not case.expected_sources:
        return EvalMetric(
            name="source_recall",
            score=1.0,
            passed=True,
            details="No expected sources configured.",
        )
    sources = " ".join(citation.source.lower() for citation in assessment.citations)
    hits = [source for source in case.expected_sources if source.lower() in sources]
    score = len(hits) / len(case.expected_sources)
    return EvalMetric(
        name="source_recall",
        score=score,
        passed=score >= 0.5,
        details=f"Matched {len(hits)}/{len(case.expected_sources)} expected sources: {hits}.",
    )


def human_review_match(case: EvalCase, assessment: ClaimAssessment) -> EvalMetric:
    if case.require_human_review is None:
        return EvalMetric(
            name="human_review_match",
            score=1.0,
            passed=True,
            details="No human-review expectation configured.",
        )
    score = 1.0 if assessment.human_review_required == case.require_human_review else 0.0
    return EvalMetric(
        name="human_review_match",
        score=score,
        passed=score == 1.0,
        details=(
            f"Expected human_review_required={case.require_human_review}, "
            f"got {assessment.human_review_required}."
        ),
    )


def agent_completion(assessment: ClaimAssessment) -> EvalMetric:
    expected_agents = {
        "Supervisor Agent",
        "Policy Agent",
        "Weather Agent",
        "Historical Claim Agent",
        "Evidence Agent",
        "Reasoning Agent",
        "Compliance Agent",
    }
    observed_agents = {finding.agent for finding in assessment.agent_findings}
    score = len(expected_agents & observed_agents) / len(expected_agents)
    return EvalMetric(
        name="agent_completion",
        score=score,
        passed=score == 1.0,
        details=f"Observed agents: {sorted(observed_agents)}.",
    )


def latency_score(latency_ms: float) -> EvalMetric:
    if latency_ms <= 15000:
        score = 1.0
    elif latency_ms <= 30000:
        score = 0.5
    else:
        score = 0.0
    return EvalMetric(
        name="latency",
        score=score,
        passed=score >= 0.5,
        details=f"Latency {latency_ms:.0f} ms.",
    )
