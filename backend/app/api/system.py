import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Company, Document, FinancialMetric, CrossDocConsistencyCheck, FinancialRisk, AuditLog
from app.evaluation.eval_dataset import EVALUATION_QUESTIONS

router = APIRouter(prefix="/system", tags=["System Metrics"])

@router.get("/metrics")
def get_system_metrics(db: Session = Depends(get_db)):
    endpoint_count = 24
    models_count = 11
    eval_dataset_size = len(EVALUATION_QUESTIONS)
    supported_formats = [".pdf", ".xlsx", ".xls", ".csv", ".docx"]
    agent_tools_count = 10
    guardrails_count = 6

    total_companies = db.query(Company).count()
    total_docs = db.query(Document).count()
    total_metrics = db.query(FinancialMetric).count()

    return {
        "status": "OPERATIONAL",
        "api_endpoints_count": endpoint_count,
        "database_models_count": models_count,
        "evaluation_dataset_size": eval_dataset_size,
        "supported_document_formats": supported_formats,
        "agent_tools_count": agent_tools_count,
        "guardrails_count": guardrails_count,
        "total_companies_indexed": total_companies,
        "total_documents_processed": total_docs,
        "total_financial_metrics_extracted": total_metrics
    }
