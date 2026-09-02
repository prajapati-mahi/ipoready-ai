from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import FinancialMetric, Company
from app.schemas.schemas import FinancialMetricResponse

router = APIRouter(prefix="/financial-metrics", tags=["Financial Metrics"])

@router.get("", response_model=List[FinancialMetricResponse])
def list_metrics(
    company_id: Optional[int] = None,
    fiscal_year: Optional[str] = None,
    metric_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FinancialMetric)
    if company_id:
        query = query.filter(FinancialMetric.company_id == company_id)
    if fiscal_year:
        query = query.filter(FinancialMetric.fiscal_year == fiscal_year)
    if metric_name:
        query = query.filter(FinancialMetric.metric_name.ilike(f"%{metric_name}%"))
    return query.order_by(FinancialMetric.id.asc()).all()
