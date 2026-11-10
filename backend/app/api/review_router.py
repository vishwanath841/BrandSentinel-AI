from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.submission import ContentSubmission, IssueFinding
from app.models.review import HumanReviewAudit
from app.schemas.submission_schema import (
    ReviewFindingActionRequest,
    FinalReviewDecisionRequest,
    SubmissionDetailResponse
)
from app.schemas.analysis_schema import IssueFindingResponse
from app.services.rewriter_service import apply_revisions_to_text
from app.api.submissions_router import get_submission

router = APIRouter(prefix="/api/review", tags=["Review & Approval"])

@router.put("/findings/{finding_id}", response_model=IssueFindingResponse)
def review_individual_finding(
    finding_id: int,
    action: ReviewFindingActionRequest,
    db: Session = Depends(get_db)
):
    finding = db.query(IssueFinding).filter(IssueFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding.review_status = action.review_status.upper()
    if action.reviewed_revision is not None:
        finding.reviewed_revision = action.reviewed_revision
    if action.reviewer_notes is not None:
        finding.reviewer_notes = action.reviewer_notes

    db.commit()
    db.refresh(finding)

    return IssueFindingResponse(
        id=finding.id,
        report_id=finding.report_id,
        category=finding.category,
        severity=finding.severity,
        flagged_text=finding.flagged_text,
        explanation=finding.explanation,
        evidence=finding.evidence or "",
        claim_status=finding.claim_status,
        suggested_revision=finding.suggested_revision or "",
        revision_rationale=finding.revision_rationale or "",
        start_char=finding.start_char,
        end_char=finding.end_char,
        review_status=finding.review_status,
        reviewed_revision=finding.reviewed_revision,
        reviewer_notes=finding.reviewer_notes
    )

@router.post("/submissions/{submission_id}/decision", response_model=SubmissionDetailResponse)
def submit_final_review_decision(
    submission_id: int,
    decision_in: FinalReviewDecisionRequest,
    db: Session = Depends(get_db)
):
    submission = db.query(ContentSubmission).filter(ContentSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    decision = decision_in.decision.upper()
    if decision not in ["APPROVED", "CHANGES_REQUESTED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED, CHANGES_REQUESTED, or REJECTED")

    submission.status = decision

    # Compute final revised content
    findings_dicts = []
    if submission.report:
        for f in submission.report.findings:
            findings_dicts.append({
                "flagged_text": f.flagged_text,
                "review_status": f.review_status,
                "suggested_revision": f.suggested_revision,
                "reviewed_revision": f.reviewed_revision
            })

    final_content = decision_in.final_content or apply_revisions_to_text(submission.extracted_text or "", findings_dicts)

    # Record immutable audit log
    audit = HumanReviewAudit(
        submission_id=submission.id,
        reviewer_name=decision_in.reviewer_name,
        reviewer_role=decision_in.reviewer_role,
        decision=decision,
        decision_notes=decision_in.decision_notes or "",
        final_content=final_content
    )
    db.add(audit)
    db.commit()

    return get_submission(submission.id, db)

