from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class IssueFindingResponse(BaseModel):
    id: int
    report_id: int
    category: str # TERMINOLOGY, CLAIM_GUARD, TONE, VISUAL, ACCESSIBILITY, MESSAGING
    severity: str # CRITICAL, HIGH, MEDIUM, LOW
    flagged_text: str
    explanation: str
    evidence: Optional[str] = ""
    claim_status: Optional[str] = None # VERIFIED, CONTRADICTION, UNSUPPORTED_NEEDS_REVIEW, COMPLIANT
    suggested_revision: Optional[str] = ""
    revision_rationale: Optional[str] = ""
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    review_status: str = "PENDING" # PENDING, ACCEPTED, EDITED, REJECTED
    reviewed_revision: Optional[str] = None
    reviewer_notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AnalysisReportResponse(BaseModel):
    id: int
    submission_id: int
    overall_score: float
    tone_score: float
    terminology_score: float
    fact_score: float
    visual_score: float
    risk_level: str
    summary: str
    visual_details: Dict[str, Any] = {}
    engine_used: str
    created_at: datetime
    findings: List[IssueFindingResponse] = []
    model_config = ConfigDict(from_attributes=True)

class QuickAnalysisRequest(BaseModel):
    brand_id: int
    text: str
    title: Optional[str] = "Quick Check"
    creator_name: Optional[str] = "Copywriter"
    intended_channel: Optional[str] = "General"

class BrandDriftMetricsResponse(BaseModel):
    total_submissions: int
    average_compliance_score: float
    approved_count: int
    pending_count: int
    changes_requested_count: int
    rejected_count: int
    top_recurring_violations: List[Dict[str, Any]]
    unsupported_claims_summary: List[Dict[str, Any]]
    tone_slip_frequency: List[Dict[str, Any]]
    guideline_gap_recommendations: List[Dict[str, str]]

class SettingsResponse(BaseModel):
    app_name: str
    version: str
    gemini_api_key_configured: bool
    gemini_model: str
    active_engine: str
    backup_keys_configured: bool = False
    custom_endpoint_configured: bool = False
    custom_llm_api_key_configured: bool = False
    local_llm_enabled: bool = False
    local_llm_endpoint: str = ""
    local_llm_model: str = ""
    local_llm_reachable: bool = False

class SettingsUpdateRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    gemini_backup_keys: Optional[str] = None
    gemini_model: Optional[str] = "gemini-2.5-flash"
    custom_llm_endpoint: Optional[str] = None
    custom_llm_api_key: Optional[str] = None
    local_llm_enabled: Optional[bool] = None
    local_llm_endpoint: Optional[str] = None
    local_llm_model: Optional[str] = None

