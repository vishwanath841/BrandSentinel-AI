import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.brand import BrandProfile
from app.models.submission import ContentSubmission, AnalysisReport, IssueFinding
from app.models.review import HumanReviewAudit
from app.schemas.submission_schema import (
    SubmissionResponse,
    SubmissionDetailResponse,
    HumanReviewAuditResponse
)
from app.schemas.analysis_schema import (
    AnalysisReportResponse,
    IssueFindingResponse
)
from app.services.extractor_service import extract_content
from app.services.inspection_service import run_comprehensive_inspection

router = APIRouter(prefix="/api/submissions", tags=["Submissions"])

@router.get("", response_model=List[SubmissionResponse])
def list_submissions(
    brand_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ContentSubmission)
    if brand_id:
        query = query.filter(ContentSubmission.brand_id == brand_id)
    if status:
        query = query.filter(ContentSubmission.status == status)
    
    subs = query.order_by(ContentSubmission.created_at.desc()).all()
    results = []
    for s in subs:
        score = s.report.overall_score if s.report else None
        risk = s.report.risk_level if s.report else None
        results.append(
            SubmissionResponse(
                id=s.id,
                brand_id=s.brand_id,
                title=s.title,
                content_type=s.content_type,
                original_filename=s.original_filename,
                creator_name=s.creator_name,
                intended_channel=s.intended_channel,
                status=s.status,
                created_at=s.created_at,
                overall_score=score,
                risk_level=risk
            )
        )
    return results

@router.get("/{submission_id}", response_model=SubmissionDetailResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    s = db.query(ContentSubmission).filter(ContentSubmission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")

    report_resp = None
    if s.report:
        findings_resp = [
            IssueFindingResponse(
                id=f.id,
                report_id=f.report_id,
                category=f.category,
                severity=f.severity,
                flagged_text=f.flagged_text,
                explanation=f.explanation,
                evidence=f.evidence or "",
                claim_status=f.claim_status,
                suggested_revision=f.suggested_revision or "",
                revision_rationale=f.revision_rationale or "",
                start_char=f.start_char,
                end_char=f.end_char,
                review_status=f.review_status,
                reviewed_revision=f.reviewed_revision,
                reviewer_notes=f.reviewer_notes
            )
            for f in s.report.findings
        ]
        
        report_resp = AnalysisReportResponse(
            id=s.report.id,
            submission_id=s.report.submission_id,
            overall_score=s.report.overall_score,
            tone_score=s.report.tone_score,
            terminology_score=s.report.terminology_score,
            fact_score=s.report.fact_score,
            visual_score=s.report.visual_score,
            risk_level=s.report.risk_level,
            summary=s.report.summary,
            visual_details=s.report.visual_details,
            engine_used=s.report.engine_used,
            created_at=s.report.created_at,
            findings=findings_resp
        )

    reviews_resp = [
        HumanReviewAuditResponse(
            id=r.id,
            submission_id=r.submission_id,
            reviewer_name=r.reviewer_name,
            reviewer_role=r.reviewer_role,
            decision=r.decision,
            decision_notes=r.decision_notes or "",
            final_content=r.final_content or "",
            created_at=r.created_at
        )
        for r in s.reviews
    ]

    return SubmissionDetailResponse(
        id=s.id,
        brand_id=s.brand_id,
        title=s.title,
        content_type=s.content_type,
        original_filename=s.original_filename,
        creator_name=s.creator_name,
        intended_channel=s.intended_channel,
        status=s.status,
        created_at=s.created_at,
        extracted_text=s.extracted_text or "",
        overall_score=s.report.overall_score if s.report else None,
        risk_level=s.report.risk_level if s.report else None,
        report=report_resp,
        reviews=reviews_resp
    )

@router.post("", response_model=SubmissionDetailResponse)
async def create_submission(
    brand_id: int = Form(...),
    title: str = Form(...),
    creator_name: str = Form("Content Creator"),
    intended_channel: str = Form("General Marketing"),
    text_content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    brand = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    content_type = "TEXT"
    file_path = None
    original_filename = None
    extracted_text = (text_content or "").strip()

    if file and file.filename:
        original_filename = file.filename
        ext = Path(original_filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}_{original_filename}"
        dest_path = settings.upload_dir / unique_name

        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_path = str(dest_path)

        if ext == ".pdf":
            content_type = "PDF"
        elif ext in [".docx", ".doc"]:
            content_type = "DOCX"
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            content_type = "IMAGE"
        else:
            content_type = "TEXT"

        # Extract content
        try:
            extracted_text, _ = extract_content(file_path, content_type)
        except Exception as e:
            if not extracted_text:
                extracted_text = f"[Extraction note: {str(e)}]"

    # If pure text submission with no file
    if not extracted_text and not file_path:
        raise HTTPException(status_code=400, detail="Either text content or a valid file must be provided")

    submission = ContentSubmission(
        brand_id=brand.id,
        title=title,
        content_type=content_type,
        original_filename=original_filename,
        file_path=file_path,
        extracted_text=extracted_text,
        creator_name=creator_name,
        intended_channel=intended_channel,
        status="PENDING_REVIEW"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Automatically run BrandSentinel inspection pipeline
    run_comprehensive_inspection(db, submission, brand)

    return get_submission(submission.id, db)

@router.delete("/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    s = db.query(ContentSubmission).filter(ContentSubmission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if s.file_path and os.path.exists(s.file_path):
        try:
            os.remove(s.file_path)
        except Exception:
            pass

    db.delete(s)
    db.commit()
    return {"message": "Submission deleted successfully"}

@router.delete("")
def delete_all_submissions(brand_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(ContentSubmission)
    if brand_id:
        query = query.filter(ContentSubmission.brand_id == brand_id)
    subs = query.all()
    count = len(subs)
    for s in subs:
        if s.file_path and os.path.exists(s.file_path):
            try:
                os.remove(s.file_path)
            except Exception:
                pass
        db.delete(s)
    db.commit()
    return {"message": f"Successfully deleted {count} submission(s)", "deleted_count": count}

@router.post("/{submission_id}/reinspect", response_model=SubmissionDetailResponse)
def reinspect_submission(submission_id: int, db: Session = Depends(get_db)):
    s = db.query(ContentSubmission).filter(ContentSubmission.id == submission_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")

    brand = s.brand
    # Delete old report
    if s.report:
        db.delete(s.report)
        db.commit()

    run_comprehensive_inspection(db, s, brand)
    return get_submission(submission_id, db)

