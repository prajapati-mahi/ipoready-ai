from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import IPOReadinessScore, Company, Document, FinancialMetric, CrossDocConsistencyCheck, FinancialRisk
from app.schemas.schemas import IPOReadinessResponse
from app.financial.ipo_readiness_scorer import IPOReadinessScorer

router = APIRouter(prefix="/ipo-readiness", tags=["IPO Readiness"])

@router.get("/{company_id}", response_model=IPOReadinessResponse)
def get_readiness_score(company_id: int, db: Session = Depends(get_db)):
    score = db.query(IPOReadinessScore).filter(IPOReadinessScore.company_id == company_id).order_by(IPOReadinessScore.id.desc()).first()
    if not score:
        # Calculate if not present
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        docs = db.query(Document).filter(Document.company_id == company_id).all()
        metrics = [m.__dict__ for m in db.query(FinancialMetric).filter(FinancialMetric.company_id == company_id).all()]
        inconsistencies = [inc.__dict__ for inc in db.query(CrossDocConsistencyCheck).filter(CrossDocConsistencyCheck.company_id == company_id).all()]
        risks = [r.__dict__ for r in db.query(FinancialRisk).filter(FinancialRisk.company_id == company_id).all()]

        res = IPOReadinessScorer.calculate_readiness(docs, metrics, inconsistencies, risks, company_id)
        score = IPOReadinessScore(
            company_id=company_id,
            overall_score=res["overall_score"],
            financial_completeness_score=res["financial_completeness_score"],
            financial_consistency_score=res["financial_consistency_score"],
            profitability_score=res["profitability_score"],
            cashflow_score=res["cashflow_score"],
            debt_health_score=res["debt_health_score"],
            growth_score=res["growth_score"],
            document_coverage_score=res["document_coverage_score"],
            breakdown_details=res["breakdown_details"]
        )
        db.add(score)
        db.commit()
        db.refresh(score)
    return score
