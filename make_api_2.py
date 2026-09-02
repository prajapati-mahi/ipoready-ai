# -*- coding: utf-8 -*-
import os

app_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\backend\app"

def write_f(rel_path, code):
    p = os.path.join(app_root, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")
    print(f"Created: {rel_path}")

# 1. Financial Metrics API
write_f("api/financial_metrics.py", """
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
""")

# 2. Chat / AI Analyst API
write_f("api/chat.py", """
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Company, FinancialMetric, DocumentChunk, CrossDocConsistencyCheck, AuditLog
from app.schemas.schemas import ChatMessageRequest, ChatResponse
from app.agent.analyst_agent import AnalystAgent
from app.guardrails.guardrails import FinancialGuardrail

router = APIRouter(prefix="/chat", tags=["AI Analyst"])

@router.post("", response_model=ChatResponse)
def chat_with_analyst(payload: ChatMessageRequest, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == payload.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    metrics_db = db.query(FinancialMetric).filter(FinancialMetric.company_id == company.id).all()
    metrics = [
        {
            "metric_name": m.metric_name,
            "raw_value_str": m.raw_value_str,
            "normalized_value_inr": m.normalized_value_inr,
            "fiscal_year": m.fiscal_year,
            "source_document_name": m.source_document_name,
            "source_page": m.source_page,
            "source_cell_ref": m.source_cell_ref,
            "confidence_score": m.confidence_score
        }
        for m in metrics_db
    ]

    chunks_db = db.query(DocumentChunk).join(DocumentChunk.document).filter(DocumentChunk.document.has(company_id=company.id)).all()
    chunks = [
        {
            "document_id": ch.document_id,
            "page_number": ch.page_number,
            "chunk_text": ch.chunk_text,
            "embedding": ch.embedding,
            "chunk_metadata": ch.chunk_metadata
        }
        for ch in chunks_db
    ]

    inconsistencies_db = db.query(CrossDocConsistencyCheck).filter(CrossDocConsistencyCheck.company_id == company.id).all()
    inconsistencies = [
        {
            "metric_name": inc.metric_name,
            "fiscal_year": inc.fiscal_year,
            "source_a_doc_name": inc.source_a_doc_name,
            "source_a_value_raw": inc.source_a_value_raw,
            "source_b_doc_name": inc.source_b_doc_name,
            "source_b_value_raw": inc.source_b_value_raw,
            "variance_percentage": inc.variance_percentage
        }
        for inc in inconsistencies_db
    ]

    # Run Autonomous Agent
    resp_dict = AnalystAgent.answer_query(
        query=payload.query,
        company_name=company.name,
        metrics=metrics,
        chunks=chunks,
        inconsistencies=inconsistencies
    )

    # Apply Strict Guardrails
    resp_dict = FinancialGuardrail.audit_response(resp_dict, chunks)

    # Persist Audit Trail
    audit = AuditLog(
        company_id=company.id,
        action_type="AI_ANALYST_QUERY",
        query_text=payload.query,
        steps_executed=[
            {"step": "Query Classification", "status": "COMPLETED"},
            {"step": "Tool Selection & Execution", "tools": [t["tool_name"] for t in resp_dict["tools_executed"]]},
            {"step": "Deterministic Financial Math", "calculations": resp_dict["calculations"]},
            {"step": "Guardrail Verification", "status": resp_dict["guardrail_status"]}
        ],
        tools_used=resp_dict["tools_executed"],
        calculations=resp_dict["calculations"],
        final_output=resp_dict["answer"],
        latency_ms=resp_dict["latency_ms"]
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    resp_dict["audit_log_id"] = audit.id
    return resp_dict
""")

# 3. IPO Readiness API
write_f("api/ipo_readiness.py", """
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
""")

# 4. Financial Risks API
write_f("api/risks.py", """
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
""")

# 5. Consistency Checks API
write_f("api/consistency.py", """
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
""")

# 6. Evaluations API
write_f("api/evaluations.py", """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Company, FinancialMetric, DocumentChunk, CrossDocConsistencyCheck
from app.evaluation.eval_runner import EvaluationHarness
from app.evaluation.eval_dataset import EVALUATION_QUESTIONS

router = APIRouter(prefix="/evaluations", tags=["Evaluation Framework"])

@router.get("/benchmark")
def get_benchmark_questions():
    return {
        "dataset_size": len(EVALUATION_QUESTIONS),
        "questions": EVALUATION_QUESTIONS
    }

@router.post("/run")
def run_evaluation_benchmark(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    metrics_db = db.query(FinancialMetric).filter(FinancialMetric.company_id == company.id).all()
    metrics = [
        {
            "metric_name": m.metric_name,
            "raw_value_str": m.raw_value_str,
            "normalized_value_inr": m.normalized_value_inr,
            "fiscal_year": m.fiscal_year,
            "source_document_name": m.source_document_name,
            "source_page": m.source_page,
            "source_cell_ref": m.source_cell_ref,
            "confidence_score": m.confidence_score
        }
        for m in metrics_db
    ]

    chunks_db = db.query(DocumentChunk).join(DocumentChunk.document).filter(DocumentChunk.document.has(company_id=company.id)).all()
    chunks = [
        {
            "document_id": ch.document_id,
            "page_number": ch.page_number,
            "chunk_text": ch.chunk_text,
            "embedding": ch.embedding,
            "chunk_metadata": ch.chunk_metadata
        }
        for ch in chunks_db
    ]

    inconsistencies_db = db.query(CrossDocConsistencyCheck).filter(CrossDocConsistencyCheck.company_id == company.id).all()
    inconsistencies = [
        {
            "metric_name": inc.metric_name,
            "fiscal_year": inc.fiscal_year,
            "source_a_doc_name": inc.source_a_doc_name,
            "source_a_value_raw": inc.source_a_value_raw,
            "source_b_doc_name": inc.source_b_doc_name,
            "source_b_value_raw": inc.source_b_value_raw,
            "variance_percentage": inc.variance_percentage
        }
        for inc in inconsistencies_db
    ]

    benchmark_report = EvaluationHarness.run_benchmark(
        company_name=company.name,
        metrics=metrics,
        chunks=chunks,
        inconsistencies=inconsistencies
    )
    return benchmark_report
""")

# 7. Reviews API
write_f("api/reviews.py", """
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import ReviewQueueItem, ReviewStatus
from app.schemas.schemas import ReviewQueueResponse, ReviewActionRequest

router = APIRouter(prefix="/reviews", tags=["Human Review Queue"])

@router.get("", response_model=List[ReviewQueueResponse])
def list_review_items(company_id: int, db: Session = Depends(get_db)):
    items = db.query(ReviewQueueItem).filter(ReviewQueueItem.company_id == company_id).order_by(ReviewQueueItem.id.desc()).all()
    return items

@router.post("/{item_id}/action", response_model=ReviewQueueResponse)
def process_review_action(item_id: int, action_in: ReviewActionRequest, db: Session = Depends(get_db)):
    item = db.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")
    
    item.review_status = action_in.action
    item.notes = action_in.notes
    if action_in.modified_payload:
        item.modified_payload = action_in.modified_payload
    item.reviewed_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(item)
    return item
""")

# 8. Audit Logs API
write_f("api/audit_logs.py", """
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import AuditLog
from app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(company_id: int, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).filter(AuditLog.company_id == company_id).order_by(AuditLog.id.desc()).limit(50).all()
    return logs
""")

# 9. Demo & System API
write_f("api/demo.py", """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.demo.seeder import DemoSeeder
from app.schemas.schemas import CompanyResponse

router = APIRouter(prefix="/demo", tags=["Demo Management"])

@router.post("/seed", response_model=CompanyResponse)
def seed_demo(db: Session = Depends(get_db)):
    company = DemoSeeder.seed_demo_company(db, settings.UPLOAD_DIR)
    return company
""")

write_f("api/system.py", """
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
""")

print("All API modules created.")
