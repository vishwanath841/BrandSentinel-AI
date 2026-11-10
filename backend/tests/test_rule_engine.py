import pytest
from app.models.brand import BrandRule
from app.services.rule_engine import evaluate_deterministic_rules

def test_deterministic_rules_forbidden_term():
    rule = BrandRule(
        id=1,
        brand_id=1,
        category="TERMINOLOGY",
        rule_name="No Jargon",
        preferred_term="integrated architecture",
        severity="HIGH",
        is_active=True
    )
    rule.forbidden_terms = ["synergy", "game-changing"]

    text = "Our company achieves great synergy through game-changing solutions."
    result = evaluate_deterministic_rules(text, [rule])

    assert result["violations_count"] == 2
    assert result["score"] < 100.0
    flagged = [f["flagged_text"].lower() for f in result["findings"]]
    assert "synergy" in flagged
    assert "game-changing" in flagged

def test_word_boundaries_prevent_false_positives():
    rule = BrandRule(
        id=2,
        brand_id=1,
        category="TERMINOLOGY",
        rule_name="No Slang",
        preferred_term="going to",
        severity="LOW",
        is_active=True
    )
    rule.forbidden_terms = ["go"]

    # "algorithm" contains "go" inside it, but word boundary should not flag it
    text = "Our algorithm executes quickly."
    result = evaluate_deterministic_rules(text, [rule])
    assert result["violations_count"] == 0
    assert result["score"] == 100.0

