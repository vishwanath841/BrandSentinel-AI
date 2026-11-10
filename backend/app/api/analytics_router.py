from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.analysis_schema import BrandDriftMetricsResponse
from app.services.analytics_service import compute_brand_drift_analytics

router = APIRouter(prefix="/api/analytics", tags=["Brand Drift Analytics"])

@router.get("/brand-drift", response_model=BrandDriftMetricsResponse)
def get_brand_drift(brand_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Returns aggregated Brand Drift analytics, recurring rule violations,
    unsupported claim hotspots, and proactive guideline gap recommendations.
    """
    return compute_brand_drift_analytics(db, brand_id)

