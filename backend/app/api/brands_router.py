from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import uuid
from pathlib import Path
from app.database import get_db
from app.config import settings
from app.models.brand import BrandProfile, BrandRule, ApprovedFact
from app.schemas.brand_schema import (
    BrandProfileResponse,
    BrandProfileDetailResponse,
    BrandProfileCreate,
    BrandRuleCreate,
    BrandRuleResponse,
    ApprovedFactCreate,
    ApprovedFactResponse
)
from app.services.extractor_service import extract_content
from app.services.gemini_service import extract_brand_guidelines_with_gemini
from app.services.local_llm_service import extract_guidelines_with_local_llm
from app.services.dynamic_guideline_parser import parse_brand_guidelines_dynamically

router = APIRouter(prefix="/api/brands", tags=["Brands"])

@router.get("", response_model=List[BrandProfileResponse])
def get_brands(db: Session = Depends(get_db)):
    brands = db.query(BrandProfile).order_by(BrandProfile.id.asc()).all()
    results = []
    for b in brands:
        resp = BrandProfileResponse(
            id=b.id,
            name=b.name,
            slug=b.slug,
            industry=b.industry,
            tagline=b.tagline or "",
            mission=b.mission or "",
            target_audience=b.target_audience or "",
            voice_traits=b.voice_traits,
            avoided_tones=b.avoided_tones,
            primary_color=b.primary_color,
            secondary_color=b.secondary_color,
            accent_color=b.accent_color,
            background_color=b.background_color,
            text_color=b.text_color,
            color_tolerance=b.color_tolerance,
            logo_path=b.logo_path,
            created_at=b.created_at,
            updated_at=b.updated_at,
            rules_count=len(b.rules),
            facts_count=len(b.approved_facts)
        )
        results.append(resp)
    return results

@router.get("/{brand_id}", response_model=BrandProfileDetailResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    b = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    rules = [
        BrandRuleResponse(
            id=r.id,
            brand_id=r.brand_id,
            category=r.category,
            rule_name=r.rule_name,
            description=r.description or "",
            preferred_term=r.preferred_term or "",
            forbidden_terms=r.forbidden_terms,
            severity=r.severity,
            rationale=r.rationale or "",
            is_active=r.is_active,
            created_at=r.created_at
        )
        for r in b.rules
    ]

    facts = [
        ApprovedFactResponse(
            id=f.id,
            brand_id=f.brand_id,
            claim_topic=f.claim_topic,
            approved_text=f.approved_text,
            metrics=f.metrics,
            verification_source=f.verification_source or "",
            last_verified_date=f.last_verified_date or "",
            is_active=f.is_active,
            created_at=f.created_at
        )
        for f in b.approved_facts
    ]

    return BrandProfileDetailResponse(
        id=b.id,
        name=b.name,
        slug=b.slug,
        industry=b.industry,
        tagline=b.tagline or "",
        mission=b.mission or "",
        target_audience=b.target_audience or "",
        voice_traits=b.voice_traits,
        avoided_tones=b.avoided_tones,
        primary_color=b.primary_color,
        secondary_color=b.secondary_color,
        accent_color=b.accent_color,
        background_color=b.background_color,
        text_color=b.text_color,
        color_tolerance=b.color_tolerance,
        logo_path=b.logo_path,
        created_at=b.created_at,
        updated_at=b.updated_at,
        rules_count=len(rules),
        facts_count=len(facts),
        rules=rules,
        approved_facts=facts
    )

@router.post("", response_model=BrandProfileDetailResponse)
def create_brand(brand_in: BrandProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(BrandProfile).filter(BrandProfile.name == brand_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Brand name already exists")
    
    b = BrandProfile(
        name=brand_in.name,
        slug=brand_in.slug.lower().replace(" ", "-"),
        industry=brand_in.industry,
        tagline=brand_in.tagline,
        mission=brand_in.mission,
        target_audience=brand_in.target_audience,
        primary_color=brand_in.primary_color,
        secondary_color=brand_in.secondary_color,
        accent_color=brand_in.accent_color,
        background_color=brand_in.background_color,
        text_color=brand_in.text_color,
        color_tolerance=brand_in.color_tolerance
    )
    b.voice_traits = brand_in.voice_traits
    b.avoided_tones = brand_in.avoided_tones
    db.add(b)
    db.commit()
    db.refresh(b)

    # Add initial rules if provided
    for r in (brand_in.rules or []):
        rule = BrandRule(
            brand_id=b.id,
            category=r.category,
            rule_name=r.rule_name,
            description=r.description or "",
            preferred_term=r.preferred_term or "",
            severity=r.severity,
            rationale=r.rationale or "",
            is_active=r.is_active
        )
        rule.forbidden_terms = r.forbidden_terms
        db.add(rule)

    # Add initial facts if provided
    for f in (brand_in.approved_facts or []):
        fact = ApprovedFact(
            brand_id=b.id,
            claim_topic=f.claim_topic,
            approved_text=f.approved_text,
            verification_source=f.verification_source or "",
            last_verified_date=f.last_verified_date or "",
            is_active=f.is_active
        )
        fact.metrics = f.metrics
        db.add(fact)

    db.commit()
    db.refresh(b)
    return get_brand(b.id, db)

@router.delete("/{brand_id}")
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    b = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Brand not found")
    db.delete(b)
    db.commit()
    return {"message": f"Brand {b.name} deleted successfully"}

@router.post("/{brand_id}/rules", response_model=BrandRuleResponse)
def add_brand_rule(brand_id: int, rule_in: BrandRuleCreate, db: Session = Depends(get_db)):
    b = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    rule = BrandRule(
        brand_id=b.id,
        category=rule_in.category,
        rule_name=rule_in.rule_name,
        description=rule_in.description or "",
        preferred_term=rule_in.preferred_term or "",
        severity=rule_in.severity,
        rationale=rule_in.rationale or "",
        is_active=rule_in.is_active
    )
    rule.forbidden_terms = rule_in.forbidden_terms
    db.add(rule)
    db.commit()
    db.refresh(rule)

    return BrandRuleResponse(
        id=rule.id,
        brand_id=rule.brand_id,
        category=rule.category,
        rule_name=rule.rule_name,
        description=rule.description or "",
        preferred_term=rule.preferred_term or "",
        forbidden_terms=rule.forbidden_terms,
        severity=rule.severity,
        rationale=rule.rationale or "",
        is_active=rule.is_active,
        created_at=rule.created_at
    )

@router.delete("/rules/{rule_id}")
def delete_brand_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(BrandRule).filter(BrandRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}

@router.post("/{brand_id}/facts", response_model=ApprovedFactResponse)
def add_approved_fact(brand_id: int, fact_in: ApprovedFactCreate, db: Session = Depends(get_db)):
    b = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    fact = ApprovedFact(
        brand_id=b.id,
        claim_topic=fact_in.claim_topic,
        approved_text=fact_in.approved_text,
        verification_source=fact_in.verification_source or "",
        last_verified_date=fact_in.last_verified_date or "",
        is_active=fact_in.is_active
    )
    fact.metrics = fact_in.metrics
    db.add(fact)
    db.commit()
    db.refresh(fact)

    return ApprovedFactResponse(
        id=fact.id,
        brand_id=fact.brand_id,
        claim_topic=fact.claim_topic,
        approved_text=fact.approved_text,
        metrics=fact.metrics,
        verification_source=fact.verification_source or "",
        last_verified_date=fact.last_verified_date or "",
        is_active=fact.is_active,
        created_at=fact.created_at
    )

@router.delete("/facts/{fact_id}")
def delete_approved_fact(fact_id: int, db: Session = Depends(get_db)):
    fact = db.query(ApprovedFact).filter(ApprovedFact.id == fact_id).first()
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    db.delete(fact)
    db.commit()
    return {"message": "Approved fact deleted successfully"}

@router.post("/extract-guidelines")
async def extract_guidelines_from_file(file: UploadFile = File(...)):
    """
    Ingest a PDF or DOCX brand guideline document and extract structured Brand DNA.
    """
    filename = file.filename or f"guideline_{uuid.uuid4().hex[:8]}"
    ext = Path(filename).suffix.lower()
    temp_path = settings.upload_dir / f"temp_{uuid.uuid4().hex}{ext}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        content_type = "PDF" if ext == ".pdf" else "DOCX" if ext in [".docx", ".doc"] else "TEXT"
        text, meta = extract_content(str(temp_path), content_type)
        
        # Tier 1: Try Gemini extraction if key is present
        extracted = extract_brand_guidelines_with_gemini(text)
        # Tier 2: Try Local LLM if Gemini didn't work
        if not extracted:
            extracted = extract_guidelines_with_local_llm(text)
        # Tier 3: Dynamic semantic guideline extraction from actual document content
        if not extracted:
            extracted = parse_brand_guidelines_dynamically(text, filename)

        return {
            "success": True,
            "filename": filename,
            "extracted_text_preview": text[:500] + ("..." if len(text) > 500 else ""),
            "brand_profile": extracted
        }
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass

