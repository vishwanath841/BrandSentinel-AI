from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class HumanReviewAudit(Base):
    __tablename__ = "human_review_audits"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("content_submissions.id"), nullable=False)
    reviewer_name = Column(String(100), nullable=False)
    reviewer_role = Column(String(80), default="Brand Manager")
    decision = Column(String(40), nullable=False) # APPROVED, CHANGES_REQUESTED, REJECTED
    decision_notes = Column(Text, default="")
    final_content = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now)

    submission = relationship("ContentSubmission", back_populates="reviews")

