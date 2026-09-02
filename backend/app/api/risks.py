from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import FinancialRisk
from app.schemas.schemas import FinancialRiskResponse

router = APIRouter(prefix="/risks", tags=["Financial Risks"])

@router.get("/{company_id}", response_model=List[FinancialRiskResponse])
def get_company_risks(company_id: int, db: Session = Depends(get_db)):
    risks = db.query(FinancialRisk).filter(FinancialRisk.company_id == company_id).all()
    return risks
