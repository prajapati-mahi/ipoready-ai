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
