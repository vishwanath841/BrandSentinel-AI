import pytest
from app.database import SessionLocal, Base, engine
from app.main import health_check
from app.api.brands_router import get_brands, create_brand
from app.api.submissions_router import list_submissions
from app.api.review_router import review_individual_finding, submit_final_review_decision
from app.api.analytics_router import get_brand_drift
from app.api.settings_router import get_settings_status
from app.schemas.brand_schema import BrandProfileCreate
from app.schemas.submission_schema import ReviewFindingActionRequest, FinalReviewDecisionRequest
from app.models.submission import ContentSubmission
from app.services.inspection_service import run_comprehensive_inspection

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_health_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert res["app"] == "BrandSentinel AI"

def test_get_brands_endpoint(db):
    brands = get_brands(db)
    assert len(brands) >= 2
    names = [b.name for b in brands]
    assert "ApexCloud Enterprise" in names

import uuid

def test_create_custom_brand(db):
    unique_suffix = uuid.uuid4().hex[:6]
    custom_brand = BrandProfileCreate(
        name=f"QuantumAI Labs {unique_suffix}",
        slug=f"quantumai-{unique_suffix}",
        industry="Artificial Intelligence",
        tagline="Empowering Intelligent Decisions",
        primary_color="#6366F1",
        voice_traits=["Innovative", "Precise"],
        avoided_tones=["Slang", "Aggressive"]
    )
    b = create_brand(custom_brand, db)
    assert b.id is not None
    assert f"QuantumAI Labs {unique_suffix}" in b.name

def test_end_to_end_submission_and_human_review(db):
    brands = get_brands(db)
    apex = [b for b in brands if b.name == "ApexCloud Enterprise"][0]

    # Create submission
    sub = ContentSubmission(
        brand_id=apex.id,
        title="Automated Test Campaign",
        content_type="TEXT",
        creator_name="Test Copywriter",
        intended_channel="Twitter / X",
        extracted_text="Our magic cloud provides guaranteed zero downtime and 100% bug-free delivery.",
        status="PENDING_REVIEW"
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    # Run inspection
    from app.models.brand import BrandProfile
    apex_model = db.query(BrandProfile).filter(BrandProfile.id == apex.id).first()
    report = run_comprehensive_inspection(db, sub, apex_model)
    
    assert report.overall_score < 100.0
    assert len(report.findings) >= 2
    finding = report.findings[0]

    # Review finding: Accept suggestion
    action = ReviewFindingActionRequest(
        review_status="ACCEPTED",
        reviewer_notes="Approved brand replacement"
    )
    reviewed_finding = review_individual_finding(finding.id, action, db)
    assert reviewed_finding.review_status == "ACCEPTED"

    # Final review decision
    decision_req = FinalReviewDecisionRequest(
        reviewer_name="Sarah Approver",
        reviewer_role="Brand Governance Director",
        decision="APPROVED",
        decision_notes="All revisions reviewed and accepted."
    )
    final_res = submit_final_review_decision(sub.id, decision_req, db)
    assert final_res.status == "APPROVED"
    assert len(final_res.reviews) >= 1
    assert final_res.reviews[0].decision == "APPROVED"

def test_analytics_brand_drift(db):
    metrics = get_brand_drift(None, db)
    total = metrics["total_submissions"] if isinstance(metrics, dict) else metrics.total_submissions
    avg_score = metrics["average_compliance_score"] if isinstance(metrics, dict) else metrics.average_compliance_score
    recs = metrics["guideline_gap_recommendations"] if isinstance(metrics, dict) else metrics.guideline_gap_recommendations
    assert total >= 1
    assert avg_score > 0
    assert len(recs) >= 1

def test_settings_endpoint():
    status = get_settings_status()
    assert status.app_name == "BrandSentinel AI"
    assert any(tag in status.active_engine for tag in ["GEMINI_HYBRID", "LOCAL_LLM", "CONTEXTUAL_SEMANTIC_ENGINE", "DETERMINISTIC_RULES"])
