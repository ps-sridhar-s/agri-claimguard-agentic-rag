from src.schemas import ClaimRequest, Recommendation


def test_normalized_query_empty():
    claim = ClaimRequest()
    assert claim.normalized_query() == "Assess crop insurance claim eligibility."


def test_normalized_query_with_fields():
    claim = ClaimRequest(
        farmer_name="Asha",
        district="Karnataka",
        crop="rice",
        date_of_loss="2026-06-01",
        loss_reason="drought",
        policy_id="POL123",
    )
    normalized = claim.normalized_query()
    assert "farmer Asha" in normalized
    assert "district Karnataka" in normalized
    assert "crop rice" in normalized
    assert "loss reason drought" in normalized
    assert "policy POL123" in normalized


def test_recommendation_enum_values():
    assert Recommendation.eligible.value == "Eligible"
    assert Recommendation.not_eligible.value == "Not Eligible"
    assert Recommendation.needs_review.value == "Needs Review"
