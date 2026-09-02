from typing import List, Dict, Any
from app.models.models import RiskSeverity, ReviewStatus

class ConsistencyAuditor:
    @staticmethod
    def audit_metrics(metrics: List[Dict[str, Any]], company_id: int) -> List[Dict[str, Any]]:
        inconsistencies = []
        grouped = {}
        for m in metrics:
            key = (m.get("metric_name"), m.get("fiscal_year"))
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(m)

        for (metric_name, fiscal_year), doc_metrics in grouped.items():
            if len(doc_metrics) < 2:
                continue

            for i in range(len(doc_metrics)):
                for j in range(i + 1, len(doc_metrics)):
                    m1 = doc_metrics[i]
                    m2 = doc_metrics[j]

                    if m1.get("source_document_name") == m2.get("source_document_name"):
                        continue

                    val1 = m1.get("normalized_value_inr", 0.0)
                    val2 = m2.get("normalized_value_inr", 0.0)

                    if val1 == 0 and val2 == 0:
                        continue

                    variance_amt = abs(val1 - val2)
                    avg_val = (abs(val1) + abs(val2)) / 2.0
                    variance_pct = round((variance_amt / avg_val) * 100.0, 2) if avg_val > 0 else 0.0

                    if variance_pct > 0.5:
                        severity = RiskSeverity.CRITICAL if variance_pct > 10.0 else RiskSeverity.HIGH if variance_pct > 3.0 else RiskSeverity.MEDIUM
                        inconsistencies.append({
                            "company_id": company_id,
                            "metric_name": metric_name,
                            "fiscal_year": fiscal_year,
                            "source_a_doc_name": m1.get("source_document_name"),
                            "source_a_page_or_cell": f"Page {m1.get('source_page')}" if m1.get("source_page") else m1.get("source_cell_ref", "N/A"),
                            "source_a_value_raw": m1.get("raw_value_str"),
                            "source_a_value_normalized": val1,
                            "source_b_doc_name": m2.get("source_document_name"),
                            "source_b_page_or_cell": f"Page {m2.get('source_page')}" if m2.get("source_page") else m2.get("source_cell_ref", "N/A"),
                            "source_b_value_raw": m2.get("raw_value_str"),
                            "source_b_value_normalized": val2,
                            "variance_amount": variance_amt,
                            "variance_percentage": variance_pct,
                            "severity": severity,
                            "status": ReviewStatus.PENDING,
                            "resolution_notes": f"Variance of {variance_pct}% between {m1.get('source_document_name')} ({m1.get('raw_value_str')}) and {m2.get('source_document_name')} ({m2.get('raw_value_str')}). Requires merchant banker review."
                        })

        return inconsistencies
