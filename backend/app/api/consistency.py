from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import CrossDocConsistencyCheck
from app.schemas.schemas import ConsistencyCheckResponse

router = APIRouter(prefix="/consistency-checks", tags=["Consistency Auditor"])

@router.get("/{company_id}", response_model=List[ConsistencyCheckResponse])
def get_consistency_checks(company_id: int, db: Session = Depends(get_db)):
    checks = db.query(CrossDocConsistencyCheck).filter(CrossDocConsistencyCheck.company_id == company_id).all()
    return checks
