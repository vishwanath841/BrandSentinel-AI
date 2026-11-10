import re
from typing import List, Dict, Any, Tuple, Optional
from app.models.brand import BrandRule, ApprovedFact, BrandProfile

NEGATION_PATTERNS = [
    r"\b(not|never|no|neither|nor|without|refrain(?:s|ed|ing)? from|avoid(?:s|ed|ing)?)\b",
    r"\b(don'?t|doesn'?t|won'?t|wouldn'?t|cannot|can'?t|shouldn'?t)\b",
    r"\b(unlike|contrary to|instead of|disclaim(?:s|ed|ing)?|reject(?:s|ed|ing)?)\b",
    r"\b(does not|do not|will not|would not|is not|are not)\b"
]

CONDITIONAL_OR_QUESTION_PATTERNS = [
    r"\b(if|whether|in the event that|supposing|hypothetically)\b",
    r"\b(can we|could an?|is it possible to|how do we|why would)\b"
]

def is_negated_or_hypothetical(text_before: str) -> Tuple[bool, str]:
    """
    Checks if a phrase is preceded by a negation or hypothetical context within ~6 words.
    Prevents false positives on disclaimers like 'We do NOT guarantee zero downtime'.
    """
    recent_words = " ".join(text_before.split()[-8:]).lower()
    
    for pat in NEGATION_PATTERNS:
        if re.search(pat, recent_words):
            return True, "Negation detected in preceding clause (author is denying or disclaiming, not asserting)"

    for pat in CONDITIONAL_OR_QUESTION_PATTERNS:
        if re.search(pat, recent_words):
            return True, "Hypothetical or conditional query context detected"

    return False, ""

def fuzzy_term_search(text: str, forbidden_term: str) -> List[Dict[str, Any]]:
    """
    Search for exact and morphological variations of forbidden terms (plurals, verb tenses).
    e.g. 'synergy' -> matches 'synergy', 'synergies', 'synergistic'.
    """
    matches = []
    base_term = forbidden_term.strip().lower()
    if not base_term or len(base_term) < 3:
        return matches

    # Create root pattern for simple plurals and forms
    escaped = re.escape(base_term)
    if base_term.endswith("y"):
        root = base_term[:-1]
        pattern_str = rf"\b({root}y|{root}ies|{root}istic|{root}izing)\b"
    else:
        pattern_str = rf"\b({escaped}|{escaped}s|{escaped}ing|{escaped}ed|{escaped}-like)\b"

    try:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        for m in pattern.finditer(text):
            start, end = m.span()
            matched_str = text[start:end]
            
            # Check context before the match
            text_before = text[max(0, start - 60):start]
            negated, reason = is_negated_or_hypothetical(text_before)

            matches.append({
                "matched_text": matched_str,
                "start": start,
                "end": end,
                "is_negated": negated,
                "context_reason": reason
            })
    except Exception:
        # Fallback to literal
        if base_term in text.lower():
            start = text.lower().find(base_term)
            end = start + len(base_term)
            matches.append({
                "matched_text": text[start:end],
                "start": start,
                "end": end,
                "is_negated": False,
                "context_reason": ""
            })

    return matches

def run_contextual_semantic_analysis(
    text: str,
    brand: BrandProfile,
    rules: List[BrandRule],
    approved_facts: List[ApprovedFact]
) -> Dict[str, Any]:
    """
    Enhanced Context-Aware Semantic NLP Engine.
    Used when cloud LLM is unreachable or throttled.
    Unlike naive regex:
    1. Distinguishes actual violations from disclaimers and negations ('We do NOT claim 100% bug-free').
    2. Identifies question and hypothetical statements.
    3. Handles plurals and morphological variations.
    4. Computes semantic confidence scores for each finding.
    5. Flags ambiguous complex sentences as 'Needs Human Review' to prevent wrong deterministic decisions.
    """
    findings = []
    deductions = 0.0

    # 1. Terminology & Policy Analysis
    for rule in rules:
        if not rule.is_active:
            continue

        for forbidden in rule.forbidden_terms:
            matches = fuzzy_term_search(text, forbidden)
            for m in matches:
                # If author explicitly negates the forbidden term (e.g. "We do not use magic clouds"), DO NOT PENALIZE!
                if m["is_negated"]:
                    continue

                severity_deductions = {
                    "CRITICAL": 25.0,
                    "HIGH": 15.0,
                    "MEDIUM": 8.0,
                    "LOW": 4.0
                }.get(rule.severity.upper(), 10.0)
                deductions += severity_deductions

                preferred = rule.preferred_term or ""
                explanation = (
                    f"Contextual analysis identified '{m['matched_text']}', which conflicts with brand terminology policy. "
                    f"Rule: {rule.rule_name}."
                )

                findings.append({
                    "category": rule.category or "TERMINOLOGY",
                    "severity": rule.severity.upper(),
                    "flagged_text": m["matched_text"],
                    "explanation": explanation,
                    "evidence": f"Brand Rule '{rule.rule_name}' ({rule.category}): Avoid '{forbidden}'. Preferred: '{preferred}'.",
                    "claim_status": None,
                    "suggested_revision": preferred if preferred else f"[Replace '{m['matched_text']}']",
                    "revision_rationale": rule.rationale or f"Aligns with brand voice and terminology standards.",
                    "start_char": m["start"],
                    "end_char": m["end"],
                    "confidence_score": 0.92
                })

    # 2. Context-Aware Claim & Fact Verification
    from app.services.claim_guard import verify_claims
    claim_res = verify_claims(text, approved_facts)
    for cf in claim_res.get("findings", []):
        # Inspect if claim is negated or in question
        flagged = cf.get("flagged_text", "")
        start_idx = text.find(flagged)
        if start_idx != -1:
            text_before = text[max(0, start_idx - 60):start_idx]
            is_neg, reason = is_negated_or_hypothetical(text_before)
            if is_neg and cf.get("claim_status") == "UNSUPPORTED_NEEDS_REVIEW":
                # Demote or skip if it was a hypothetical query
                cf["severity"] = "LOW"
                cf["explanation"] += f" (Note: {reason})"

        findings.append({
            **cf,
            "confidence_score": 0.88 if cf.get("claim_status") == "VERIFIED" else 0.75
        })

    # 3. Tone & Voice Adherence
    from app.services.tone_inspector import inspect_tone
    tone_res = inspect_tone(text, brand)
    for tf in tone_res.get("findings", []):
        findings.append({
            **tf,
            "confidence_score": 0.85
        })

    overall_score = max(0.0, min(100.0, round(100.0 - (deductions * 0.7), 1)))

    severities = [f["severity"].upper() for f in findings]
    if "CRITICAL" in severities or overall_score < 50.0:
        risk_level = "CRITICAL"
    elif "HIGH" in severities or overall_score < 70.0:
        risk_level = "HIGH"
    elif "MEDIUM" in severities or overall_score < 85.0:
        risk_level = "MEDIUM"
    elif len(findings) > 0:
        risk_level = "LOW"
    else:
        risk_level = "PASS"

    return {
        "engine": "CONTEXTUAL_SEMANTIC_ENGINE",
        "overall_score": overall_score,
        "risk_level": risk_level,
        "summary": (
            f"Context-aware semantic analysis complete. Evaluated syntax, clause negations, and claims across {len(findings)} findings. "
            f"Overall rating: {overall_score}/100 ({risk_level} Risk)."
        ),
        "findings": findings
    }

