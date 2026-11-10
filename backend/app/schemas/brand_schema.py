from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class BrandRuleBase(BaseModel):
    category: str = "TERMINOLOGY" # TERMINOLOGY, MESSAGING, LEGAL, COMPETITOR, STYLE
    rule_name: str
    description: Optional[str] = ""
    preferred_term: Optional[str] = ""
    forbidden_terms: List[str] = []
    severity: str = "HIGH" # CRITICAL, HIGH, MEDIUM, LOW
    rationale: Optional[str] = ""
    is_active: bool = True

class BrandRuleCreate(BrandRuleBase):
    pass

class BrandRuleResponse(BrandRuleBase):
    id: int
    brand_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApprovedFactBase(BaseModel):
    claim_topic: str
    approved_text: str
    metrics: Dict[str, Any] = {}
    verification_source: Optional[str] = ""
    last_verified_date: Optional[str] = ""
    is_active: bool = True

class ApprovedFactCreate(ApprovedFactBase):
    pass

class ApprovedFactResponse(ApprovedFactBase):
    id: int
    brand_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BrandProfileBase(BaseModel):
    name: str
    slug: str
    industry: Optional[str] = "Technology"
    tagline: Optional[str] = ""
    mission: Optional[str] = ""
    target_audience: Optional[str] = ""
    voice_traits: List[str] = []
    avoided_tones: List[str] = []
    primary_color: str = "#1E3A8A"
    secondary_color: str = "#0284C7"
    accent_color: str = "#10B981"
    background_color: str = "#FFFFFF"
    text_color: str = "#0F172A"
    color_tolerance: float = 40.0
    logo_path: Optional[str] = None

class BrandProfileCreate(BrandProfileBase):
    rules: Optional[List[BrandRuleCreate]] = []
    approved_facts: Optional[List[ApprovedFactCreate]] = []

class BrandProfileResponse(BrandProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    rules_count: int = 0
    facts_count: int = 0
    model_config = ConfigDict(from_attributes=True)

class BrandProfileDetailResponse(BrandProfileResponse):
    rules: List[BrandRuleResponse] = []
    approved_facts: List[ApprovedFactResponse] = []
    model_config = ConfigDict(from_attributes=True)

