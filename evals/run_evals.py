from __future__ import annotations

import argparse
import json
from pathlib import Path

from agents.claim_workflow import ClaimAssessmentService
from evals.evaluator import run_eval_suite
from evals.ragas_evaluation import ragas_status, to_ragas_rows
from src.knowledge_base import KnowledgeBase
from src.schemas import EvalCase


def load_cases(path: Path) -> list[EvalCase]:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return [EvalCase.model_validate(item) for item in payload]


def main():
    parser = argparse.ArgumentParser(description="Run AgriClaimGuard evaluation suite.")
    parser.add_argument(
        "--cases",
        default="evals/sample_cases.json",
        help="Path to eval cases JSON.",
    )
    parser.add_argument(
        "--source-dir",
        default="data_source",
        help="Document source directory.",
    )
    parser.add_argument(
        "--output",
        default="storage/eval_reports/latest_eval_report.json",
        help="Path to write JSON eval report.",
    )
    parser.add_argument(
        "--ragas-output",
        default="storage/eval_reports/latest_ragas_rows.json",
        help="Path to write RAGAS-compatible rows.",
    )
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    kb = KnowledgeBase(source_dir=args.source_dir).build()
    service = ClaimAssessmentService(kb)
    report = run_eval_suite(cases, service)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(mode="json"), f, indent=2)

    ragas_output = Path(args.ragas_output)
    ragas_output.parent.mkdir(parents=True, exist_ok=True)
    with open(ragas_output, "w", encoding="utf-8") as f:
        json.dump(to_ragas_rows(report.results), f, indent=2)

    print(f"Eval cases: {report.total_cases}")
    print(f"Passed: {report.passed_cases}/{report.total_cases}")
    print(f"Average score: {report.average_score:.2f}")
    print(f"Metrics: {json.dumps(report.metrics_summary, indent=2)}")
    print(f"Report saved: {output}")
    print(f"RAGAS rows saved: {ragas_output}")
    print(f"RAGAS status: {ragas_status()['message']}")


if __name__ == "__main__":
    main()

