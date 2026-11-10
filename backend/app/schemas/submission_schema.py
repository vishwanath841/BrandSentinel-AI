from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.analysis_schema import AnalysisReportResponse

class SubmissionCreate(BaseModel):
    brand_id: int
    title: str
    content_type: str = "TEXT" # TEXT, PDF, DOCX, IMAGE
    text_content: Optional[str] = ""
    creator_name: Optional[str] = "Content Creator"
    intended_channel: Optional[str] = "Social Media"

class SubmissionResponse(BaseModel):
    id: int
    brand_id: int
    title: str
    content_type: str
    original_filename: Optional[str] = None
    creator_name: str
    intended_channel: str
    status: str
    created_at: datetime
    overall_score: Optional[float] = None
    risk_level: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class HumanReviewAuditResponse(BaseModel):
    id: int
    submission_id: int
    reviewer_name: str
    reviewer_role: str
    decision: str
    decision_notes: Optional[str] = ""
    final_content: Optional[str] = ""
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SubmissionDetailResponse(SubmissionResponse):
    extracted_text: Optional[str] = ""
    report: Optional[AnalysisReportResponse] = None
    reviews: List[HumanReviewAuditResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ReviewFindingActionRequest(BaseModel):
    review_status: str # ACCEPTED, EDITED, REJECTED
    reviewed_revision: Optional[str] = None
    reviewer_notes: Optional[str] = None

class FinalReviewDecisionRequest(BaseModel):
    reviewer_name: str = "Brand Manager"
    reviewer_role: str = "Brand Governance Lead"
    decision: str # APPROVED, CHANGES_REQUESTED, REJECTED
    decision_notes: Optional[str] = ""
    final_content: Optional[str] = ""

