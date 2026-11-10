import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.brand import BrandProfile, BrandRule, ApprovedFact
from app.models.submission import ContentSubmission, AnalysisReport, IssueFinding
from app.services.rule_engine import evaluate_deterministic_rules
from app.services.claim_guard import verify_claims
from app.services.tone_inspector import inspect_tone
from app.services.visual_inspector import inspect_visual_assets
from app.services.gemini_service import analyze_with_gemini, get_active_gemini_key
from app.services.local_llm_service import analyze_with_local_llm, is_local_llm_available
from app.services.semantic_engine import run_contextual_semantic_analysis

def run_comprehensive_inspection(
    db: Session,
    submission: ContentSubmission,
    brand: BrandProfile
) -> AnalysisReport:
    """
    Executes the full BrandSentinel AI inspection pipeline:
    1. Deterministic Rule Engine (Terminology & Restrictions)
    2. ClaimGuard (Fact verification & unsupported claims)
    3. Tone & Voice Inspector
    4. Visual Brand Inspector (if image)
    5. Gemini LLM hybrid enhancement (if API key active)
    6. Risk prioritization and score synthesis
    """
    text = submission.extracted_text or ""
    all_findings = []

    # 1. Deterministic Rule Engine
    rule_results = evaluate_deterministic_rules(text, brand.rules)
    all_findings.extend(rule_results["findings"])
    term_score = rule_results["score"]

    # 2. ClaimGuard
    claim_results = verify_claims(text, brand.approved_facts)
    all_findings.extend(claim_results["findings"])
    fact_score = claim_results["score"]

    # 3. Tone Inspector
    tone_results = inspect_tone(text, brand)
    all_findings.extend(tone_results["findings"])
    tone_score = tone_results["score"]

    # 4. Visual Inspection (if image submission)
    visual_score = 100.0
    visual_details = {}
    if submission.content_type == "IMAGE" and submission.file_path and os.path.exists(submission.file_path):
        visual_res = inspect_visual_assets(
            image_path=submission.file_path,
            brand_primary=brand.primary_color,
            brand_secondary=brand.secondary_color,
            brand_accent=brand.accent_color,
            brand_background=brand.background_color,
            tolerance=brand.color_tolerance
        )
        visual_score = visual_res["visual_score"]
        visual_details = visual_res
        all_findings.extend(visual_res["issues"])

    # 5. Hybrid Inspection Dispatch:
    #    Tier 1: Cloud Gemini API (if key configured)
    #    Tier 2: Local LLM — Ollama / LM Studio (if LOCAL_LLM_ENABLED and server reachable)
    #    Tier 3: Contextual Semantic NLP Engine (always works, zero external deps)
    engine_used = "CONTEXTUAL_SEMANTIC_ENGINE (Local NLP)"
    gemini_key = get_active_gemini_key()
    llm_result = None  # will hold result from Tier 1 or Tier 2

    # Build brand context dicts once (shared by both LLM tiers)
    brand_ctx = {
        "name": brand.name,
        "industry": brand.industry,
        "voice_traits": brand.voice_traits,
        "avoided_tones": brand.avoided_tones
    }
    rules_ctx = [
        {
            "rule_name": r.rule_name,
            "category": r.category,
            "preferred_term": r.preferred_term,
            "forbidden_terms": r.forbidden_terms,
            "severity": r.severity,
            "rationale": r.rationale
        }
        for r in brand.rules if r.is_active
    ]
    facts_ctx = [
        {
            "claim_topic": f.claim_topic,
            "approved_text": f.approved_text,
            "verification_source": f.verification_source
        }
        for f in brand.approved_facts if f.is_active
    ]

    # TIER 1: Gemini Cloud
    if gemini_key and text:
        llm_result = analyze_with_gemini(text, brand_ctx, rules_ctx, facts_ctx)

    # TIER 2: Local LLM (Ollama / LM Studio) — only if Tier 1 didn't produce a result
    if llm_result is None and text and is_local_llm_available():
        llm_result = analyze_with_local_llm(text, brand_ctx, rules_ctx, facts_ctx)

    if llm_result:
        model_name = llm_result.get("engine_model_used", "unknown")
        if model_name.startswith("local:"):
            engine_used = f"LOCAL_LLM ({model_name})"
        else:
            engine_used = f"GEMINI_HYBRID ({model_name})"
        print(f"Inspection Engine: successfully used {engine_used}", flush=True)
        # Incorporate LLM findings if unique
        existing_flagged = {f["flagged_text"].lower() for f in all_findings}
        for gf in llm_result.get("findings", []):
            flagged = gf.get("flagged_text", "").strip()
            if flagged and flagged.lower() not in existing_flagged:
                all_findings.append({
                    "category": gf.get("category", "TONE"),
                    "severity": gf.get("severity", "MEDIUM"),
                    "flagged_text": flagged,
                    "explanation": gf.get("explanation", ""),
                    "evidence": gf.get("evidence", f"LLM Deep Contextual Inspection ({model_name})"),
                    "claim_status": gf.get("claim_status"),
                    "suggested_revision": gf.get("suggested_revision", ""),
                    "revision_rationale": gf.get("revision_rationale", "")
                })
                existing_flagged.add(flagged.lower())
        
        # Blend scores
        if "overall_score" in llm_result:
            term_score = round((term_score * 0.5) + (llm_result.get("terminology_score", term_score) * 0.5), 1)
            fact_score = round((fact_score * 0.5) + (llm_result.get("fact_score", fact_score) * 0.5), 1)
            tone_score = round((tone_score * 0.5) + (llm_result.get("tone_score", tone_score) * 0.5), 1)
    else:
        # TIER 3: Context-Aware Semantic NLP Engine (Evaluates clause negations & disclaimers)
        semantic_res = run_contextual_semantic_analysis(text, brand, brand.rules, brand.approved_facts)
        engine_used = "CONTEXTUAL_SEMANTIC_ENGINE (Local NLP)"
        print(f"Inspection Engine: using {engine_used}", flush=True)
        # Merge semantic insights
        existing_flagged = {f["flagged_text"].lower() for f in all_findings}
        for sf in semantic_res.get("findings", []):
            flagged = sf.get("flagged_text", "").strip()
            if flagged and flagged.lower() not in existing_flagged:
                all_findings.append(sf)
                existing_flagged.add(flagged.lower())

    # Calculate overall compliance score
    if submission.content_type == "IMAGE":
        overall_score = round(
            (visual_score * 0.5) + (term_score * 0.2) + (fact_score * 0.15) + (tone_score * 0.15),
            1
        )
    else:
        overall_score = round(
            (term_score * 0.35) + (fact_score * 0.35) + (tone_score * 0.30),
            1
        )

    # Determine risk level
    severities = [f["severity"].upper() for f in all_findings]
    if "CRITICAL" in severities or overall_score < 50.0:
        risk_level = "CRITICAL"
    elif "HIGH" in severities or overall_score < 70.0:
        risk_level = "HIGH"
    elif "MEDIUM" in severities or overall_score < 85.0:
        risk_level = "MEDIUM"
    elif len(all_findings) > 0 or overall_score < 95.0:
        risk_level = "LOW"
    else:
        risk_level = "PASS"

    # Use AI-synthesized narrative summary if available, or generate rich dynamic briefing
    summary = ""
    if llm_result and llm_result.get("summary"):
        summary = llm_result.get("summary").strip()
    
    if not summary:
        violations_desc = []
        term_violations = [f for f in all_findings if f.get("category") == "TERMINOLOGY"]
        claim_violations = [f for f in all_findings if f.get("category") == "CLAIM_GUARD"]
        tone_violations = [f for f in all_findings if f.get("category") == "TONE"]
        comp_violations = [f for f in all_findings if f.get("category") == "COMPETITOR"]

        if comp_violations:
            violations_desc.append(f"{len(comp_violations)} competitor disparagement risk(s)")
        if term_violations:
            violations_desc.append(f"{len(term_violations)} prohibited terminology deviation(s)")
        if claim_violations:
            violations_desc.append(f"{len(claim_violations)} unverified or conflicting claim(s)")
        if tone_violations:
            violations_desc.append(f"{len(tone_violations)} tone inconsistency issue(s)")

        issues_phrase = ", ".join(violations_desc) if violations_desc else "no critical policy violations"
        word_count = len(text.split())
        content_desc = f"uploaded {submission.content_type.lower()}" if submission.content_type != "TEXT" else "submitted content"
        
        summary = (
            f"Governance evaluation for '{submission.title}' ({word_count} words across {submission.intended_channel}) "
            f"concluded against {brand.name} brand standards. The inspection identified {issues_phrase}, "
            f"resulting in an overall compliance rating of {overall_score}/100 ({risk_level} Risk). "
            f"Review the prioritized findings, accept intent-preserving revisions to align with corporate voice, "
            f"and complete human reviewer sign-off prior to external release."
        )

    # Create AnalysisReport record
    report = AnalysisReport(
        submission_id=submission.id,
        overall_score=overall_score,
        tone_score=tone_score,
        terminology_score=term_score,
        fact_score=fact_score,
        visual_score=visual_score,
        risk_level=risk_level,
        summary=summary,
        visual_details=visual_details,
        engine_used=engine_used
    )
    db.add(report)
    db.flush() # populate report.id

    # Add IssueFindings
    for f in all_findings:
        finding = IssueFinding(
            report_id=report.id,
            category=f.get("category", "TERMINOLOGY"),
            severity=f.get("severity", "MEDIUM"),
            flagged_text=f.get("flagged_text", ""),
            explanation=f.get("explanation", ""),
            evidence=f.get("evidence", ""),
            claim_status=f.get("claim_status"),
            suggested_revision=f.get("suggested_revision", ""),
            revision_rationale=f.get("revision_rationale", ""),
            start_char=f.get("start_char"),
            end_char=f.get("end_char"),
            review_status="PENDING"
        )
        db.add(finding)

    db.commit()
    db.refresh(report)
    return report

