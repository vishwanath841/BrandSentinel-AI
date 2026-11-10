import pytest
from app.models.brand import BrandProfile, BrandRule, ApprovedFact
from app.services.semantic_engine import is_negated_or_hypothetical, run_contextual_semantic_analysis

def test_negation_detection():
    negated, reason = is_negated_or_hypothetical("We explicitly do not promise")
    assert negated is True

    not_negated, _ = is_negated_or_hypothetical("We are proud to provide")
    assert not_negated is False

def test_disclaimer_not_falsely_penalized():
    """
    Ensures disclaimers like 'We do not use magic cloud' are not falsely flagged
    as violations by the contextual semantic analyzer.
    """
    brand = BrandProfile(
        id=1,
        name="ApexCloud Enterprise",
        primary_color="#1E3A8A"
    )
    brand.voice_traits = ["Authoritative"]
    brand.avoided_tones = ["Aggressive"]

    rule = BrandRule(
        id=1,
        brand_id=1,
        category="TERMINOLOGY",
        rule_name="Approved Product Nomenclature",
        preferred_term="ApexCloud Data Fabric",
        severity="HIGH",
        is_active=True
    )
    rule.forbidden_terms = ["magic cloud"]

    # This text contains a disclaimer ("we do not use magic cloud")
    text_with_disclaimer = "Our engineering team clarifies that we do not use magic cloud solutions."
    
    res = run_contextual_semantic_analysis(text_with_disclaimer, brand, [rule], [])
    
    # The forbidden term was negated by "do not", so it should NOT be flagged as an active violation!
    flagged_terms = [f["flagged_text"] for f in res["findings"] if f["category"] == "TERMINOLOGY"]
    assert "magic cloud" not in flagged_terms

