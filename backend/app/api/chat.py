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
