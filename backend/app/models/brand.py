import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    industry = Column(String(100), default="Technology")
    tagline = Column(String(255), default="")
    mission = Column(Text, default="")
    target_audience = Column(Text, default="")
    voice_traits_json = Column(Text, default="[]")       # JSON array of approved tones
    avoided_tones_json = Column(Text, default="[]")      # JSON array of prohibited tones
    primary_color = Column(String(10), default="#1E3A8A") # Hex code
    secondary_color = Column(String(10), default="#0284C7")
    accent_color = Column(String(10), default="#10B981")
    background_color = Column(String(10), default="#FFFFFF")
    text_color = Column(String(10), default="#0F172A")
    color_tolerance = Column(Float, default=40.0)
    logo_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    rules = relationship("BrandRule", back_populates="brand", cascade="all, delete-orphan")
    approved_facts = relationship("ApprovedFact", back_populates="brand", cascade="all, delete-orphan")
    submissions = relationship("ContentSubmission", back_populates="brand", cascade="all, delete-orphan")

    @property
    def voice_traits(self):
        try:
            return json.loads(self.voice_traits_json or "[]")
        except Exception:
            return []

    @voice_traits.setter
    def voice_traits(self, val):
        self.voice_traits_json = json.dumps(val if isinstance(val, list) else [])

    @property
    def avoided_tones(self):
        try:
            return json.loads(self.avoided_tones_json or "[]")
        except Exception:
            return []

    @avoided_tones.setter
    def avoided_tones(self, val):
        self.avoided_tones_json = json.dumps(val if isinstance(val, list) else [])


class BrandRule(Base):
    __tablename__ = "brand_rules"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    category = Column(String(50), default="TERMINOLOGY") # TERMINOLOGY, MESSAGING, LEGAL, COMPETITOR, STYLE
    rule_name = Column(String(150), nullable=False)
    description = Column(Text, default="")
    preferred_term = Column(String(150), default="")
    forbidden_terms_json = Column(Text, default="[]")    # JSON array of forbidden strings
    severity = Column(String(20), default="HIGH")        # CRITICAL, HIGH, MEDIUM, LOW
    rationale = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    brand = relationship("BrandProfile", back_populates="rules")

    @property
    def forbidden_terms(self):
        try:
            return json.loads(self.forbidden_terms_json or "[]")
        except Exception:
            return []

    @forbidden_terms.setter
    def forbidden_terms(self, val):
        self.forbidden_terms_json = json.dumps(val if isinstance(val, list) else [])


class ApprovedFact(Base):
    __tablename__ = "approved_facts"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    claim_topic = Column(String(120), nullable=False)    # e.g., "SLA", "User Base", "Security Certification"
    approved_text = Column(Text, nullable=False)         # Exact verified claim wording
    metrics_json = Column(Text, default="{}")            # Extracted numbers/metrics e.g. {"uptime": "99.99%"}
    verification_source = Column(String(200), default="")# Source proof e.g. "Q3 2024 Audited Financials"
    last_verified_date = Column(String(50), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    brand = relationship("BrandProfile", back_populates="approved_facts")

    @property
    def metrics(self):
        try:
            return json.loads(self.metrics_json or "{}")
        except Exception:
            return {}

    @metrics.setter
    def metrics(self, val):
        self.metrics_json = json.dumps(val if isinstance(val, dict) else {})

