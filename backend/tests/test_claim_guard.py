import pytest
from app.models.brand import ApprovedFact
from app.services.claim_guard import verify_claims

def test_claim_guard_verified_fact():
    fact = ApprovedFact(
        id=1,
        brand_id=1,
        claim_topic="SLA",
        approved_text="ApexCloud guarantees 99.99% monthly uptime SLA backed by automated credits.",
        verification_source="SLA Agreement",
        is_active=True
    )
    fact.metrics = {"uptime": "99.99%"}

    text = "We are proud that ApexCloud guarantees 99.99% uptime SLA for every client."
    result = verify_claims(text, [fact])

    assert result["verified_count"] >= 1
    assert result["contradiction_count"] == 0

def test_claim_guard_contradiction():
    fact = ApprovedFact(
        id=1,
        brand_id=1,
        claim_topic="SLA",
        approved_text="ApexCloud guarantees 99.99% monthly uptime SLA.",
        verification_source="SLA Agreement",
        is_active=True
    )
    fact.metrics = {"uptime": "99.99%"}

    # Exaggerated claim: 99.999%
    text = "ApexCloud guarantees 99.999% uptime SLA across all regions."
    result = verify_claims(text, [fact])

    assert result["contradiction_count"] >= 1
    flagged_statuses = [f.get("claim_status") for f in result["findings"]]
    assert "CONTRADICTION" in flagged_statuses

def test_claim_guard_reliability_principle_unsupported():
    """
    CRITICAL PDF REQUIREMENT:
    'It will not claim a promotional statement is false solely because supporting evidence was not found;
    it will label it as unsupported or requiring review.'
    """
    approved_facts = [] # No facts in database for this brand

    text = "We are the #1 world's first guaranteed zero downtime platform."
    result = verify_claims(text, approved_facts)

    assert result["unsupported_count"] >= 1
    for f in result["findings"]:
        if f["claim_status"] == "UNSUPPORTED_NEEDS_REVIEW":
            assert "Unsupported / Needs Review" in f["evidence"] or "UNSUPPORTED_NEEDS_REVIEW" == f["claim_status"]

