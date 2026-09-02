from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Company, Document, FinancialMetric, FinancialRisk, IPOReadinessScore
from app.schemas.schemas import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=List[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    results = []
    for c in companies:
        doc_count = db.query(Document).filter(Document.company_id == c.id).count()
        metric_count = db.query(FinancialMetric).filter(FinancialMetric.company_id == c.id).count()
        risk_count = db.query(FinancialRisk).filter(FinancialRisk.company_id == c.id).count()
        latest_score = db.query(IPOReadinessScore).filter(IPOReadinessScore.company_id == c.id).order_by(IPOReadinessScore.id.desc()).first()
        
        c_dict = {
            "id": c.id,
            "name": c.name,
            "cin": c.cin,
            "sector": c.sector,
            "target_ipo_date": c.target_ipo_date,
            "description": c.description,
            "created_at": c.created_at,
            "document_count": doc_count,
            "metric_count": metric_count,
            "risk_count": risk_count,
            "readiness_score": latest_score.overall_score if latest_score else None
        }
        results.append(c_dict)
    return results

@router.post("", response_model=CompanyResponse)
def create_company(company_in: CompanyCreate, db: Session = Depends(get_db)):
    company = Company(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    doc_count = db.query(Document).filter(Document.company_id == company.id).count()
    metric_count = db.query(FinancialMetric).filter(FinancialMetric.company_id == company.id).count()
    risk_count = db.query(FinancialRisk).filter(FinancialRisk.company_id == company.id).count()
    latest_score = db.query(IPOReadinessScore).filter(IPOReadinessScore.company_id == company.id).order_by(IPOReadinessScore.id.desc()).first()

    return {
        "id": company.id,
        "name": company.name,
        "cin": company.cin,
        "sector": company.sector,
        "target_ipo_date": company.target_ipo_date,
        "description": company.description,
        "created_at": company.created_at,
        "document_count": doc_count,
        "metric_count": metric_count,
        "risk_count": risk_count,
        "readiness_score": latest_score.overall_score if latest_score else None
    }
