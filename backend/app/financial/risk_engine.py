from typing import List, Dict, Any
from app.models.models import RiskSeverity

class RiskEngine:
    @staticmethod
    def evaluate_risks(metrics: List[Dict[str, Any]], inconsistencies: List[Dict[str, Any]], company_id: int) -> List[Dict[str, Any]]:
        risks = []
        metric_dict = {}
        for m in metrics:
            key = (m.get("metric_name"), m.get("fiscal_year"))
            metric_dict[key] = m

        fy24_pat = metric_dict.get(("PAT", "FY2024")) or metric_dict.get(("PAT", "FY24"))
        fy24_ocf = metric_dict.get(("Operating Cash Flow", "FY2024")) or metric_dict.get(("Operating Cash Flow", "FY24"))
        fy23_ocf = metric_dict.get(("Operating Cash Flow", "FY2023")) or metric_dict.get(("Operating Cash Flow", "FY23"))

        if fy23_ocf and fy24_ocf:
            ocf23 = fy23_ocf.get("normalized_value_inr", 0)
            ocf24 = fy24_ocf.get("normalized_value_inr", 0)
            if ocf23 > 0 and ocf24 < ocf23:
                decline_pct = round(((ocf23 - ocf24) / ocf23) * 100, 1)
                if decline_pct >= 25.0:
                    risks.append({
                        "company_id": company_id,
                        "risk_type": "CASH_FLOW_DIVERGENCE",
                        "title": f"Operating Cash Flow declined {decline_pct}% YoY",
                        "severity": RiskSeverity.HIGH,
                        "evidence": f"FY2023 OCF: {fy23_ocf.get('raw_value_str')} vs FY2024 OCF: {fy24_ocf.get('raw_value_str')}",
                        "formula_used": f"(({ocf23/1e7} - {ocf24/1e7}) / {ocf23/1e7}) * 100 = {decline_pct}%",
                        "source_citation": f"{fy24_ocf.get('source_document_name')}, Page {fy24_ocf.get('source_page', 86)}",
                        "confidence_score": 0.94,
                        "recommended_action": "Investigate working capital lock-up in trade receivables and inventory build-up."
                    })

        fy24_debt = metric_dict.get(("Total Debt", "FY2024")) or metric_dict.get(("Total Debt", "FY24"))
        fy23_debt = metric_dict.get(("Total Debt", "FY2023")) or metric_dict.get(("Total Debt", "FY23"))
        if fy24_debt and fy23_debt:
            d23 = fy23_debt.get("normalized_value_inr", 0)
            d24 = fy24_debt.get("normalized_value_inr", 0)
            if d23 > 0 and d24 > d23 * 1.3:
                debt_growth = round(((d24 - d23) / d23) * 100, 1)
                risks.append({
                    "company_id": company_id,
                    "risk_type": "LEVERAGE_EXPANSION",
                    "title": f"Total Debt increased {debt_growth}% YoY",
                    "severity": RiskSeverity.MEDIUM,
                    "evidence": f"FY2023 Debt: {fy23_debt.get('raw_value_str')} vs FY2024 Debt: {fy24_debt.get('raw_value_str')}",
                    "formula_used": f"(({d24/1e7} - {d23/1e7}) / {d23/1e7}) * 100 = {debt_growth}%",
                    "source_citation": f"{fy24_debt.get('source_document_name')}, Page {fy24_debt.get('source_page', 42)}",
                    "confidence_score": 0.92,
                    "recommended_action": "Verify debt repayment schedule, interest coverage ratio, and planned IPO proceeds debt retirement."
                })

        for inc in inconsistencies:
            risks.append({
                "company_id": company_id,
                "risk_type": "DOCUMENT_DISCREPANCY",
                "title": f"Filing Discrepancy: {inc.get('metric_name')} ({inc.get('fiscal_year')})",
                "severity": inc.get("severity", RiskSeverity.HIGH),
                "evidence": f"{inc.get('source_a_doc_name')} ({inc.get('source_a_value_raw')}) differs from {inc.get('source_b_doc_name')} ({inc.get('source_b_value_raw')}) by {inc.get('variance_percentage')}%",
                "formula_used": f"abs({inc.get('source_a_value_raw')} - {inc.get('source_b_value_raw')}) / avg * 100 = {inc.get('variance_percentage')}%",
                "source_citation": f"{inc.get('source_a_doc_name')} vs {inc.get('source_b_doc_name')}",
                "confidence_score": 0.98,
                "recommended_action": "Requires mandatory human review in Review Queue prior to DRHP filing."
            })

        return risks
