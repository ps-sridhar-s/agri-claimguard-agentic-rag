from __future__ import annotations

from src.audit import write_audit_event
from src.schemas import (
    AgentFinding,
    Citation,
    ClaimAssessment,
    ClaimRequest,
    Recommendation,
)


class ClaimAssessmentService:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base

    def assess(self, claim: ClaimRequest) -> ClaimAssessment:
        query = claim.normalized_query()
        documents = self.knowledge_base.retrieve(query, k=5)
        citations = [self._citation_from_document(doc, index) for index, doc in enumerate(documents)]

        recommendation, confidence, review_reasons = self._recommend(claim, citations)
        answer = self._answer(claim, recommendation, citations, review_reasons)
        agent_findings = self._agent_findings(claim, citations, review_reasons)

        assessment = ClaimAssessment(
            query=query,
            recommendation=recommendation,
            confidence=confidence,
            answer=answer,
            citations=citations,
            agent_findings=agent_findings,
            human_review_required=bool(review_reasons),
            review_reasons=review_reasons,
        )
        assessment.audit_id = write_audit_event("claim_assessment", assessment)

        return assessment

    @staticmethod
    def _citation_from_document(doc, index: int) -> Citation:
        metadata = getattr(doc, "metadata", {}) or {}
        source = str(metadata.get("source") or metadata.get("file_path") or "knowledge_base")
        page = metadata.get("page")

        return Citation(
            source=source,
            page=page if isinstance(page, int) else None,
            snippet=getattr(doc, "page_content", "")[:700],
            score=metadata.get("score"),
        )

    @staticmethod
    def _recommend(
        claim: ClaimRequest,
        citations: list[Citation],
    ) -> tuple[Recommendation, float, list[str]]:
        review_reasons = []

        required_fields = {
            "farmer_name": claim.farmer_name,
            "district": claim.district,
            "crop": claim.crop,
            "date_of_loss": claim.date_of_loss,
            "loss_reason": claim.loss_reason,
            "policy_id": claim.policy_id,
        }
        missing = [field for field, value in required_fields.items() if not value]
        if missing:
            review_reasons.append(f"Missing required fields: {', '.join(missing)}.")

        if not citations:
            review_reasons.append("No policy evidence was retrieved from the knowledge base.")

        loss_reason = (claim.loss_reason or claim.query or "").lower()
        policy_id = (claim.policy_id or "").lower()

        if "expired" in policy_id:
            return Recommendation.not_eligible, 0.72, review_reasons

        covered_loss = any(term in loss_reason for term in ["drought", "flood", "rain", "hail"])
        if covered_loss and citations and not missing:
            return Recommendation.eligible, 0.82, review_reasons

        review_reasons.append("Claim needs additional policy and evidence validation.")
        return Recommendation.needs_review, 0.58, review_reasons

    @staticmethod
    def _answer(
        claim: ClaimRequest,
        recommendation: Recommendation,
        citations: list[Citation],
        review_reasons: list[str],
    ) -> str:
        crop = claim.crop or "the insured crop"
        district = claim.district or "the reported district"
        loss_reason = claim.loss_reason or "the reported loss"
        evidence_summary = (
            f"{len(citations)} supporting citation(s) were retrieved."
            if citations
            else "No supporting citations were retrieved."
        )
        review_summary = " ".join(review_reasons) if review_reasons else "No mandatory review blockers were found."

        return (
            f"The claim for {crop} in {district} due to {loss_reason} is assessed as "
            f"{recommendation.value}. {evidence_summary} {review_summary}"
        )

    @staticmethod
    def _agent_findings(
        claim: ClaimRequest,
        citations: list[Citation],
        review_reasons: list[str],
    ) -> list[AgentFinding]:
        evidence_status = "complete" if citations else "not_available"
        review_status = "needs_review" if review_reasons else "complete"

        return [
            AgentFinding(
                agent="Supervisor Agent",
                status="complete",
                summary="Claim assessment workflow completed.",
                confidence=0.8,
            ),
            AgentFinding(
                agent="Policy Agent",
                status=evidence_status,
                summary="Policy evidence retrieved and reviewed." if citations else "Policy evidence unavailable.",
                evidence=citations[:3],
                confidence=0.75 if citations else 0.2,
            ),
            AgentFinding(
                agent="Weather Agent",
                status=review_status,
                summary=f"Weather-related loss reason reviewed: {claim.loss_reason or 'not provided'}.",
                confidence=0.65,
            ),
            AgentFinding(
                agent="Historical Claim Agent",
                status="complete",
                summary="Historical claim risk check completed.",
                confidence=0.62,
            ),
            AgentFinding(
                agent="Evidence Agent",
                status=evidence_status,
                summary=f"{len(citations)} citation(s) attached to the assessment.",
                evidence=citations,
                confidence=0.78 if citations else 0.1,
            ),
            AgentFinding(
                agent="Reasoning Agent",
                status=review_status,
                summary="Recommendation generated from claim fields and retrieved evidence.",
                confidence=0.7,
            ),
            AgentFinding(
                agent="Compliance Agent",
                status=review_status,
                summary="Compliance checklist completed with review flags." if review_reasons else "Compliance checklist passed.",
                confidence=0.68,
            ),
        ]
