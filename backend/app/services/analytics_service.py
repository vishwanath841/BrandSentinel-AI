from typing import Dict, Any, List, Optional
from collections import Counter
from sqlalchemy.orm import Session
from app.models.submission import ContentSubmission, AnalysisReport, IssueFinding
from app.models.brand import BrandProfile, BrandRule

def compute_brand_drift_analytics(db: Session, brand_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Computes Brand Drift Analytics and Governance Insights across submissions.
    Identifies recurring violations and points out guideline areas that are unclear.
    """
    query = db.query(ContentSubmission)
    if brand_id:
        query = query.filter(ContentSubmission.brand_id == brand_id)
    
    submissions = query.all()
    total_submissions = len(submissions)

    if total_submissions == 0:
        return {
            "total_submissions": 0,
            "average_compliance_score": 100.0,
            "approved_count": 0,
            "pending_count": 0,
            "changes_requested_count": 0,
            "rejected_count": 0,
            "top_recurring_violations": [],
            "unsupported_claims_summary": [],
            "tone_slip_frequency": [],
            "guideline_gap_recommendations": [
                {
                    "area": "System Initialized",
                    "recommendation": "Submit content to begin tracking brand drift analytics and recurring compliance patterns."
                }
            ]
        }

    status_counts = Counter(s.status for s in submissions)
    approved_count = status_counts.get("APPROVED", 0)
    pending_count = status_counts.get("PENDING_REVIEW", 0)
    changes_requested_count = status_counts.get("CHANGES_REQUESTED", 0)
    rejected_count = status_counts.get("REJECTED", 0)

    # Gather all reports and findings
    submission_ids = [s.id for s in submissions]
    reports = db.query(AnalysisReport).filter(AnalysisReport.submission_id.in_(submission_ids)).all()
    
    total_score = sum(r.overall_score for r in reports) if reports else 100.0
    avg_score = round(total_score / len(reports), 1) if reports else 100.0

    report_ids = [r.id for r in reports]
    findings = db.query(IssueFinding).filter(IssueFinding.report_id.in_(report_ids)).all()

    # Analyze recurring violations
    terminology_counter = Counter()
    unsupported_claims_counter = Counter()
    tone_counter = Counter()

    for f in findings:
        if f.category == "TERMINOLOGY":
            terminology_counter[f.flagged_text.lower()] += 1
        elif f.category == "CLAIM_GUARD" and f.claim_status == "UNSUPPORTED_NEEDS_REVIEW":
            # Extract key snippet
            unsupported_claims_counter[f.flagged_text[:80] + "..."] += 1
        elif f.category == "TONE":
            tone_counter[f.flagged_text.lower()] += 1

    top_recurring_violations = [
        {"term": term, "count": count, "category": "Terminology"}
        for term, count in terminology_counter.most_common(5)
    ]

    unsupported_claims_summary = [
        {"claim": claim, "frequency": count, "status": "Needs Verification"}
        for claim, count in unsupported_claims_counter.most_common(5)
    ]

    tone_slip_frequency = [
        {"tone_marker": marker, "frequency": count}
        for marker, count in tone_counter.most_common(5)
    ]

    # Generate smart guideline gap recommendations
    recommendations = []
    if terminology_counter:
        top_term, top_count = terminology_counter.most_common(1)[0]
        recommendations.append({
            "area": "Terminology Clarification Needed",
            "recommendation": f"Creators repeatedly used prohibited term '{top_term}' ({top_count} times). Consider adding an explicit team memo or prominent example in the guideline doc."
        })

    if unsupported_claims_counter:
        top_claim, top_claim_count = unsupported_claims_counter.most_common(1)[0]
        recommendations.append({
            "area": "Approved Fact Coverage Gap",
            "recommendation": f"Promotional assertions regarding '{top_claim}' lack approved proof points. Legal/Product should publish an approved fact sheet for this topic."
        })

    if tone_counter:
        recommendations.append({
            "area": "Brand Persona Drift",
            "recommendation": f"Tone deviations detected {sum(tone_counter.values())} times. Provide copywriters with before/after phrasing examples in the company playbook."
        })

    if not recommendations:
        recommendations.append({
            "area": "Guideline Health",
            "recommendation": "Current submissions show strong brand adherence with minimal recurring drift."
        })

    return {
        "total_submissions": total_submissions,
        "average_compliance_score": avg_score,
        "approved_count": approved_count,
        "pending_count": pending_count,
        "changes_requested_count": changes_requested_count,
        "rejected_count": rejected_count,
        "top_recurring_violations": top_recurring_violations,
        "unsupported_claims_summary": unsupported_claims_summary,
        "tone_slip_frequency": tone_slip_frequency,
        "guideline_gap_recommendations": recommendations
    }
