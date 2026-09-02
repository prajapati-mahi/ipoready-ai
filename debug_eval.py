# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\backend")
from app.core.database import SessionLocal
from app.models.models import FinancialMetric, DocumentChunk, CrossDocConsistencyCheck
from app.agent.analyst_agent import AnalystAgent
from app.evaluation.eval_dataset import EVALUATION_QUESTIONS

db = SessionLocal()
metrics = [{"metric_name": m.metric_name, "raw_value_str": m.raw_value_str, "normalized_value_inr": m.normalized_value_inr, "fiscal_year": m.fiscal_year, "source_document_name": m.source_document_name, "source_page": m.source_page, "source_cell_ref": m.source_cell_ref, "confidence_score": m.confidence_score} for m in db.query(FinancialMetric).all()]
chunks = [{"document_id": ch.document_id, "page_number": ch.page_number, "chunk_text": ch.chunk_text, "embedding": ch.embedding, "chunk_metadata": ch.chunk_metadata} for ch in db.query(DocumentChunk).all()]
inconsistencies = [{"metric_name": inc.metric_name, "fiscal_year": inc.fiscal_year, "source_a_doc_name": inc.source_a_doc_name, "source_a_value_raw": inc.source_a_value_raw, "source_b_doc_name": inc.source_b_doc_name, "source_b_value_raw": inc.source_b_value_raw, "variance_percentage": inc.variance_percentage} for inc in db.query(CrossDocConsistencyCheck).all()]

for q in EVALUATION_QUESTIONS[:7]:
    resp = AnalystAgent.answer_query(q["question"], "Acme Technologies Private Limited", metrics, chunks, inconsistencies)
    exp = q["expected_answer"]
    clean_exp = exp.replace("₹", "").replace("Cr", "").replace("%", "").strip().lower()
    is_corr = clean_exp in resp["answer"].lower()
    print("Q:", q["question"])
    print("Exp:", exp, "| Clean:", clean_exp)
    print("Ans:", resp["answer"])
    print("Match:", is_corr)
    print("-" * 50)
