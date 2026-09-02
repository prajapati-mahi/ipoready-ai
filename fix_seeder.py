# -*- coding: utf-8 -*-
import os

app_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\backend\app"

with open(os.path.join(app_root, "demo", "seeder.py"), "w", encoding="utf-8") as f:
    f.write('''import os
import hashlib
from sqlalchemy.orm import Session
from app.models.models import (
    Company, Document, DocumentChunk,
    FinancialMetric, CrossDocConsistencyCheck, FinancialRisk,
    IPOReadinessScore, ReviewQueueItem, AuditLog, ProcessingStatus, MetricStatus, RiskSeverity, ReviewStatus
)
from app.demo.generate_synthetic_docs import SyntheticDocumentGenerator
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.excel_parser import ExcelParser
from app.ingestion.chunking import FinancialChunker
from app.financial.metric_extractor import MetricExtractor
from app.financial.consistency_auditor import ConsistencyAuditor
from app.financial.risk_engine import RiskEngine
from app.financial.ipo_readiness_scorer import IPOReadinessScorer
from app.rag.embeddings import LocalEmbeddingEngine

class DemoSeeder:
    @classmethod
    def seed_demo_company(cls, db: Session, upload_dir: str) -> Company:
        company = db.query(Company).filter(Company.name == "Acme Technologies Private Limited").first()
        if not company:
            company = Company(
                name="Acme Technologies Private Limited",
                cin="U72200MH2018PTC308912",
                sector="Enterprise SaaS & Cloud Infrastructure",
                target_ipo_date="Q4 FY2025",
                description="High-growth B2B enterprise SaaS company providing cloud automation and financial document AI solutions."
            )
            db.add(company)
            db.commit()
            db.refresh(company)

        # Check if already populated
        existing_metrics = db.query(FinancialMetric).filter(FinancialMetric.company_id == company.id).count()
        if existing_metrics > 5:
            return company

        doc_paths = SyntheticDocumentGenerator.generate_all(upload_dir)
        all_metrics = []
        all_chunks = []

        for f_path in doc_paths:
            f_name = os.path.basename(f_path)
            with open(f_path, "rb") as f:
                f_hash = hashlib.sha256(f.read()).hexdigest()

            doc_type = "Annual Report" if "Annual_Report" in f_name else "Investor Presentation" if "Investor" in f_name else "Financial Model"
            f_size = os.path.getsize(f_path)

            doc = Document(
                company_id=company.id,
                filename=f_name,
                file_path=f_path,
                file_hash=f_hash,
                document_type=doc_type,
                fiscal_year="FY2024",
                page_count=2 if f_name.endswith(".pdf") else 1,
                file_size_bytes=f_size,
                processing_status=ProcessingStatus.INDEXED,
                processing_duration_ms=185
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            if f_name.endswith(".pdf"):
                parsed = PDFParser.parse_pdf(f_path)
            else:
                parsed = ExcelParser.parse_excel(f_path)

            chunks = FinancialChunker.chunk_document(parsed, doc.id, f_name, doc_type)
            for ch in chunks:
                emb = LocalEmbeddingEngine.get_embedding(ch["chunk_text"])
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    page_number=ch.get("page_number"),
                    section_title=ch.get("section_title"),
                    chunk_index=ch.get("chunk_index"),
                    chunk_text=ch.get("chunk_text"),
                    embedding=emb,
                    token_count=ch.get("token_count"),
                    chunk_metadata=ch.get("chunk_metadata")
                )
                db.add(db_chunk)
                all_chunks.append(ch)

            extracted = MetricExtractor.extract_metrics_from_text(parsed["full_text"], f_name)
            for m in extracted:
                m_obj = FinancialMetric(
                    company_id=company.id,
                    document_id=doc.id,
                    metric_name=m["metric_name"],
                    raw_value_str=m["raw_value_str"],
                    normalized_value_inr=m["normalized_value_inr"],
                    currency=m["currency"],
                    unit=m["unit"],
                    fiscal_year=m["fiscal_year"],
                    statement_type=m["statement_type"],
                    source_document_name=m["source_document_name"],
                    source_page=m.get("source_page"),
                    confidence_score=m["confidence_score"],
                    status=MetricStatus.EXTRACTED
                )
                db.add(m_obj)
                all_metrics.append(m)

        # Seed multi-year spreadsheet metrics if not picked up by regex
        manual_metrics = [
            ("Revenue", "₹100.00 Cr", 1_000_000_000.0, "FY2023", "Acme_Tech_Financial_Model_FY22_FY24.xlsx", "Sheet P&L -> Cell C2"),
            ("Revenue", "₹78.00 Cr", 780_000_000.0, "FY2022", "Acme_Tech_Financial_Model_FY22_FY24.xlsx", "Sheet P&L -> Cell B2"),
            ("EBITDA", "₹24.00 Cr", 240_000_000.0, "FY2023", "Acme_Tech_Financial_Model_FY22_FY24.xlsx", "Sheet P&L -> Cell C6"),
            ("PAT", "₹14.20 Cr", 142_000_000.0, "FY2023", "Acme_Tech_Financial_Model_FY22_FY24.xlsx", "Sheet P&L -> Cell C12"),
            ("Operating Cash Flow", "₹40.00 Cr", 400_000_000.0, "FY2023", "Acme_Tech_Annual_Report_FY24.pdf", "Page 86"),
            ("Total Debt", "₹30.00 Cr", 300_000_000.0, "FY2023", "Acme_Tech_Annual_Report_FY24.pdf", "Page 74"),
            ("Free Cash Flow", "₹15.20 Cr", 152_000_000.0, "FY2024", "Acme_Tech_Cash_Flow_Statement.xlsx", "Sheet Cash Flow -> Cell C4"),
            ("Revenue", "₹128.00 Cr", 1_280_000_000.0, "FY2024", "Acme_Tech_Investor_Presentation_FY24.pdf", "Page 1")
        ]

        for m_name, raw_val, norm_val, fy, src_doc, ref in manual_metrics:
            m_obj = FinancialMetric(
                company_id=company.id,
                metric_name=m_name,
                raw_value_str=raw_val,
                normalized_value_inr=norm_val,
                currency="INR",
                unit="Crore",
                fiscal_year=fy,
                statement_type="P&L" if m_name in ["Revenue", "EBITDA", "PAT"] else "Cash Flow" if "Cash" in m_name else "Balance Sheet",
                source_document_name=src_doc,
                source_cell_ref=ref if "->" in ref else None,
                source_page=int(ref.replace("Page", "").strip()) if "Page" in ref else None,
                confidence_score=0.96,
                status=MetricStatus.EXTRACTED
            )
            db.add(m_obj)
            all_metrics.append({
                "metric_name": m_name,
                "raw_value_str": raw_val,
                "normalized_value_inr": norm_val,
                "fiscal_year": fy,
                "source_document_name": src_doc,
                "source_cell_ref": ref if "->" in ref else None,
                "source_page": int(ref.replace("Page", "").strip()) if "Page" in ref else None,
                "confidence_score": 0.96
            })

        db.commit()

        # Consistency Check
        inconsistencies = ConsistencyAuditor.audit_metrics(all_metrics, company.id)
        for inc in inconsistencies:
            check_obj = CrossDocConsistencyCheck(
                company_id=company.id,
                metric_name=inc["metric_name"],
                fiscal_year=inc["fiscal_year"],
                source_a_doc_name=inc["source_a_doc_name"],
                source_a_page_or_cell=inc["source_a_page_or_cell"],
                source_a_value_raw=inc["source_a_value_raw"],
                source_a_value_normalized=inc["source_a_value_normalized"],
                source_b_doc_name=inc["source_b_doc_name"],
                source_b_page_or_cell=inc["source_b_page_or_cell"],
                source_b_value_raw=inc["source_b_value_raw"],
                source_b_value_normalized=inc["source_b_value_normalized"],
                variance_amount=inc["variance_amount"],
                variance_percentage=inc["variance_percentage"],
                severity=inc["severity"],
                status=inc["status"],
                resolution_notes=inc["resolution_notes"]
            )
            db.add(check_obj)

            queue_item = ReviewQueueItem(
                company_id=company.id,
                item_type="CONSISTENCY",
                reason=f"Variance of {inc['variance_percentage']}% in {inc['metric_name']}",
                original_payload=inc,
                review_status=ReviewStatus.PENDING
            )
            db.add(queue_item)

        # Risks
        risks = RiskEngine.evaluate_risks(all_metrics, inconsistencies, company.id)
        for r in risks:
            risk_obj = FinancialRisk(
                company_id=company.id,
                risk_type=r["risk_type"],
                title=r["title"],
                severity=r["severity"],
                evidence=r["evidence"],
                formula_used=r["formula_used"],
                source_citation=r["source_citation"],
                confidence_score=r["confidence_score"],
                recommended_action=r["recommended_action"]
            )
            db.add(risk_obj)

        # IPO Readiness Score
        readiness = IPOReadinessScorer.calculate_readiness(doc_paths, all_metrics, inconsistencies, risks, company.id)
        score_obj = IPOReadinessScore(
            company_id=company.id,
            overall_score=readiness["overall_score"],
            financial_completeness_score=readiness["financial_completeness_score"],
            financial_consistency_score=readiness["financial_consistency_score"],
            profitability_score=readiness["profitability_score"],
            cashflow_score=readiness["cashflow_score"],
            debt_health_score=readiness["debt_health_score"],
            growth_score=readiness["growth_score"],
            document_coverage_score=readiness["document_coverage_score"],
            breakdown_details=readiness["breakdown_details"]
        )
        db.add(score_obj)

        audit = AuditLog(
            company_id=company.id,
            action_type="WORKSPACE_INITIALIZATION",
            query_text="Automated IPO Readiness & Document Ingestion Pipeline",
            steps_executed=[
                {"step": "Document Validation & Ingestion", "status": "COMPLETED"},
                {"step": "Multi-Format Parsing (PDF & Excel)", "status": "COMPLETED"},
                {"step": "Hybrid Vector Indexing", "status": "COMPLETED"},
                {"step": "Cross-Document Consistency Audit", "status": "FLAGGED_INCONSISTENCY"},
                {"step": "10-Point Risk Engine Execution", "status": "COMPLETED"},
                {"step": "100-Point IPO Readiness Score Generation", "status": "COMPLETED"}
            ],
            latency_ms=420
        )
        db.add(audit)
        db.commit()

        print(f"Demo company seeded successfully: {company.name}")
        return company
''')
print("Seeder updated.")
