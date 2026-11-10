import pytest
from app.services.rewriter_service import apply_revisions_to_text

def test_apply_revisions():
    original = "We leverage synergy to deliver a game-changing product."
    findings = [
        {
            "flagged_text": "synergy",
            "suggested_revision": "integrated collaboration",
            "review_status": "ACCEPTED"
        },
        {
            "flagged_text": "game-changing",
            "suggested_revision": "innovative",
            "review_status": "ACCEPTED"
        }
    ]

    revised = apply_revisions_to_text(original, findings)
    assert "synergy" not in revised
    assert "game-changing" not in revised
    assert "integrated collaboration" in revised
    assert "innovative" in revised

def test_rejected_revisions_are_not_applied():
    original = "We guarantee zero downtime."
    findings = [
        {
            "flagged_text": "guarantee zero downtime",
            "suggested_revision": "high availability",
            "review_status": "REJECTED"
        }
    ]
    revised = apply_revisions_to_text(original, findings)
    assert revised == original

