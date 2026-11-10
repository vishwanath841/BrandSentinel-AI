import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ContentSubmission(Base):
    __tablename__ = "content_submissions"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content_type = Column(String(50), default="TEXT") # TEXT, PDF, DOCX, IMAGE
    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    extracted_text = Column(Text, default="")
    creator_name = Column(String(100), default="Content Creator")
    intended_channel = Column(String(100), default="General Marketing")
    status = Column(String(50), default="PENDING_REVIEW") # PENDING_REVIEW, APPROVED, CHANGES_REQUESTED, REJECTED
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    brand = relationship("BrandProfile", back_populates="submissions")
    report = relationship("AnalysisReport", back_populates="submission", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("HumanReviewAudit", back_populates="submission", cascade="all, delete-orphan")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("content_submissions.id"), nullable=False, unique=True)
    overall_score = Column(Float, default=100.0)       # 0 - 100
    tone_score = Column(Float, default=100.0)
    terminology_score = Column(Float, default=100.0)
    fact_score = Column(Float, default=100.0)
    visual_score = Column(Float, default=100.0)
    risk_level = Column(String(30), default="PASS")     # PASS, LOW, MEDIUM, HIGH, CRITICAL
    summary = Column(Text, default="")
    visual_details_json = Column(Text, default="{}")    # Dominant colors, contrast ratio, visual flags
    engine_used = Column(String(50), default="DETERMINISTIC_RULES")
    created_at = Column(DateTime, default=utc_now)

    submission = relationship("ContentSubmission", back_populates="report")
    findings = relationship("IssueFinding", back_populates="report", cascade="all, delete-orphan")

    @property
    def visual_details(self):
        try:
            return json.loads(self.visual_details_json or "{}")
        except Exception:
            return {}

    @visual_details.setter
    def visual_details(self, val):
        self.visual_details_json = json.dumps(val if isinstance(val, dict) else {})


class IssueFinding(Base):
    __tablename__ = "issue_findings"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("analysis_reports.id"), nullable=False)
    category = Column(String(50), nullable=False)      # TERMINOLOGY, CLAIM_GUARD, TONE, VISUAL, ACCESSIBILITY, MESSAGING
    severity = Column(String(20), default="MEDIUM")    # CRITICAL, HIGH, MEDIUM, LOW
    flagged_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    evidence = Column(Text, default="")                # Citation of rule / approved fact
    claim_status = Column(String(50), nullable=True)   # VERIFIED, CONTRADICTION, UNSUPPORTED_NEEDS_REVIEW, COMPLIANT
    suggested_revision = Column(Text, default="")      # Intent-preserving revision
    revision_rationale = Column(Text, default="")      # Why the suggestion works
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    review_status = Column(String(30), default="PENDING") # PENDING, ACCEPTED, EDITED, REJECTED
    reviewed_revision = Column(Text, nullable=True)    # If reviewer edited the suggestion
    reviewer_notes = Column(Text, nullable=True)

    report = relationship("AnalysisReport", back_populates="findings")

