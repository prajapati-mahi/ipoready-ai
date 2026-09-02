import pytest
from app.financial.consistency_auditor import ConsistencyAuditor

def test_detect_inconsistency():
    metrics = [
        {"metric_name": "Revenue", "fiscal_year": "FY2024", "source_document_name": "Annual_Report.pdf", "raw_value_str": "₹125 Cr", "normalized_value_inr": 1_250_000_000.0},
        {"metric_name": "Revenue", "fiscal_year": "FY2024", "source_document_name": "Investor_Presentation.pdf", "raw_value_str": "₹128 Cr", "normalized_value_inr": 1_280_000_000.0}
    ]
    inconsistencies = ConsistencyAuditor.audit_metrics(metrics, company_id=1)
    assert len(inconsistencies) == 1
    assert inconsistencies[0]["variance_percentage"] == 2.37 or round(inconsistencies[0]["variance_percentage"], 1) == 2.4
