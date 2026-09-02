# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\backend")

from app.core.database import SessionLocal, Base, engine
from app.demo.seeder import DemoSeeder
from app.core.config import settings
from app.evaluation.eval_runner import EvaluationHarness
from app.models.models import FinancialMetric, DocumentChunk, CrossDocConsistencyCheck

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("Seeding demo company...")
company = DemoSeeder.seed_demo_company(db, settings.UPLOAD_DIR)
print(f"Seeded company: {company.name} (ID: {company.id})")

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
    for m in db.query(FinancialMetric).filter(FinancialMetric.company_id == company.id).all()
]

chunks = [
    {
        "document_id": ch.document_id,
        "page_number": ch.page_number,
        "chunk_text": ch.chunk_text,
        "embedding": ch.embedding,
        "chunk_metadata": ch.chunk_metadata
    }
    for ch in db.query(DocumentChunk).all()
]

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
    for inc in db.query(CrossDocConsistencyCheck).filter(CrossDocConsistencyCheck.company_id == company.id).all()
]

print(f"Extracted {len(metrics)} metrics and {len(chunks)} document chunks.")
print("Running Evaluation Benchmark on 35 Golden Questions...")
report = EvaluationHarness.run_benchmark(company.name, metrics, chunks, inconsistencies)

print(f"-> Total Evaluated: {report['total_evaluated']}")
print(f"-> Answer Accuracy: {report['answer_accuracy_pct']}%")
print(f"-> Citation Accuracy: {report['citation_accuracy_pct']}%")
print(f"-> Retrieval Precision: {report['retrieval_precision_pct']}%")
print(f"-> Hallucination Rate: {report['hallucination_rate_pct']}%")
print(f"-> Average Latency: {report['average_latency_ms']} ms")
print("TEST SEED & BENCHMARK COMPLETE!")
