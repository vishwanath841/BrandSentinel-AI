import re
from typing import List, Dict, Any
from app.models.brand import BrandRule

def evaluate_deterministic_rules(text: str, rules: List[BrandRule]) -> Dict[str, Any]:
    """
    Evaluate deterministic terminology and brand rules against submitted text.
    Returns findings, terminology score, and statistics.
    """
    if not text or not rules:
        return {
            "findings": [],
            "score": 100.0,
            "violations_count": 0
        }

    findings = []
    text_lower = text.lower()
    deductions = 0.0

    for rule in rules:
        if not rule.is_active:
            continue

        forbidden_list = rule.forbidden_terms
        for term in forbidden_list:
            if not term.strip():
                continue

            # Word boundary regex search (case-insensitive)
            escaped_term = re.escape(term.strip())
            pattern = re.compile(rf"\b{escaped_term}\b", re.IGNORECASE)
            
            for match in pattern.finditer(text):
                start, end = match.span()
                matched_text = text[start:end]

                # Severity deduction
                severity_weight = {
                    "CRITICAL": 30.0,
                    "HIGH": 20.0,
                    "MEDIUM": 10.0,
                    "LOW": 5.0
                }.get(rule.severity.upper(), 10.0)
                deductions += severity_weight

                # Intent-preserving suggestion
                preferred = rule.preferred_term or ""
                suggested_text = preferred if preferred else f"[Replace '{matched_text}']"

                explanation = (
                    f"'{matched_text}' violates brand terminology policy: {rule.description or rule.rule_name}."
                )
                evidence = (
                    f"Brand Rule '{rule.rule_name}' ({rule.category}): Avoid '{term}'. Use approved '{preferred}' instead."
                    if preferred else
                    f"Brand Rule '{rule.rule_name}' ({rule.category}): '{term}' is prohibited. Rationale: {rule.rationale or 'Brand compliance policy.'}"
                )

                findings.append({
                    "category": rule.category or "TERMINOLOGY",
                    "severity": rule.severity.upper(),
                    "flagged_text": matched_text,
                    "explanation": explanation,
                    "evidence": evidence,
                    "suggested_revision": suggested_text,
                    "revision_rationale": rule.rationale or f"Aligns with approved brand voice and terminology standards.",
                    "start_char": start,
                    "end_char": end,
                    "claim_status": None
                })

    # Calculate terminology score bounded between 0 and 100
    terminology_score = max(0.0, min(100.0, round(100.0 - deductions, 1)))

    return {
        "findings": findings,
        "score": terminology_score,
        "violations_count": len(findings)
    }

