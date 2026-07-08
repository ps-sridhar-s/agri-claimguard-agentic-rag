from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Recommendation(str, Enum):
    eligible = "Eligible"
    not_eligible = "Not Eligible"
    needs_review = "Needs Review"


class ClaimRequest(BaseModel):
    farmer_name: str | None = Field(default=None, description="Farmer name")
    district: str | None = Field(default=None, description="Claim district")
    crop: str | None = Field(default=None, description="Crop type")
    date_of_loss: str | None = Field(default=None, description="Date of crop loss")
    loss_reason: str | None = Field(default=None, description="Reason such as drought or flood")
    policy_id: str | None = Field(default=None, description="Policy identifier")
    query: str | None = Field(default=None, description="Free-form claim question")

    def normalized_query(self) -> str:
        if self.query:
            return self.query.strip()

        parts = [
            f"farmer {self.farmer_name}" if self.farmer_name else "",
            f"district {self.district}" if self.district else "",
            f"crop {self.crop}" if self.crop else "",
            f"date of loss {self.date_of_loss}" if self.date_of_loss else "",
            f"loss reason {self.loss_reason}" if self.loss_reason else "",
            f"policy {self.policy_id}" if self.policy_id else "",
        ]
        details = ", ".join(part for part in parts if part)
        if details:
            return f"Assess crop insurance claim eligibility for {details}."
        return "Assess crop insurance claim eligibility."


class Citation(BaseModel):
    source: str
    page: int | None = None
    snippet: str
    score: float | None = None


class AgentFinding(BaseModel):
    agent: str
    status: Literal["complete", "needs_review", "not_available"]
    summary: str
    evidence: list[Citation] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClaimAssessment(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    query: str
    recommendation: Recommendation
    confidence: float = Field(ge=0.0, le=1.0)
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    agent_findings: list[AgentFinding] = Field(default_factory=list)
    human_review_required: bool
    review_reasons: list[str] = Field(default_factory=list)
    audit_id: str | None = None


class IngestResponse(BaseModel):
    indexed_documents: int
    chunks: int
    vector_store_enabled: bool
    bm25_enabled: bool
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str = "AgriClaimGuard"
    checks: dict[str, Any]


class EvalCase(BaseModel):
    id: str
    claim: ClaimRequest
    expected_recommendation: Recommendation | None = None
    expected_sources: list[str] = Field(default_factory=list)
    expected_keywords: list[str] = Field(default_factory=list)
    require_human_review: bool | None = None


class EvalMetric(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    details: str


class EvalResult(BaseModel):
    case_id: str
    query: str
    recommendation: Recommendation
    confidence: float
    latency_ms: float
    metrics: list[EvalMetric]
    overall_score: float = Field(ge=0.0, le=1.0)
    passed: bool
    assessment: ClaimAssessment


class EvalSuiteReport(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_cases: int
    passed_cases: int
    average_score: float = Field(ge=0.0, le=1.0)
    metrics_summary: dict[str, float]
    results: list[EvalResult]
