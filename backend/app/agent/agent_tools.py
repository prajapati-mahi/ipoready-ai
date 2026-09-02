import re
from typing import Dict, Any, List, Optional
from app.financial.calculator import FinancialCalculator

class AgentToolRegistry:
    def __init__(self, metrics_repo: List[Dict[str, Any]], chunks_repo: List[Dict[str, Any]], consistency_repo: List[Dict[str, Any]]):
        self.metrics_repo = metrics_repo
        self.chunks_repo = chunks_repo
        self.consistency_repo = consistency_repo

    def search_financial_metrics(self, metric_name: str, period: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        clean_m = metric_name.lower().replace("&", "and").strip()
        for m in self.metrics_repo:
            cur_name = m.get("metric_name", "").lower().replace("&", "and").strip()
            name_match = (clean_m in cur_name) or (cur_name in clean_m)
            
            period_match = True
            if period:
                clean_p = period.upper().replace(" ", "").replace("20", "")  # FY24, FY2024 both match FY24
                clean_mp = m.get("fiscal_year", "").upper().replace(" ", "").replace("20", "")
                period_match = (clean_p in clean_mp) or (clean_mp in clean_p)
                
            if name_match and period_match:
                results.append(m)
        return results

    def get_excel_cell(self, doc_name: str, sheet_name: str, cell_ref: str) -> Dict[str, Any]:
        return {
            "source": f"{doc_name} -> Sheet '{sheet_name}' -> Cell {cell_ref}",
            "cell": cell_ref,
            "sheet": sheet_name,
            "status": "LOCATED"
        }

    def calculate_metric(self, metric_type: str, **kwargs) -> Dict[str, Any]:
        if metric_type == "yoy_growth":
            return FinancialCalculator.calculate_yoy_growth(float(kwargs.get("initial", 0)), float(kwargs.get("final", 0)))
        elif metric_type == "cagr":
            return FinancialCalculator.calculate_cagr(float(kwargs.get("initial", 0)), float(kwargs.get("final", 0)), int(kwargs.get("years", 1)))
        elif metric_type == "margin":
            return FinancialCalculator.calculate_margin(float(kwargs.get("metric_val", 0)), float(kwargs.get("revenue", 1)), kwargs.get("name", "Margin"))
        elif metric_type == "ratio":
            return FinancialCalculator.calculate_ratio(float(kwargs.get("numerator", 0)), float(kwargs.get("denominator", 1)), kwargs.get("name", "Ratio"))
        return {"error": f"Unknown calculation type {metric_type}"}

    def compare_periods(self, metric_name: str, period1: str, period2: str) -> Dict[str, Any]:
        m1 = self.search_financial_metrics(metric_name, period1)
        m2 = self.search_financial_metrics(metric_name, period2)
        if not m1 or not m2:
            return {"error": f"Could not find {metric_name} for both {period1} and {period2}"}
        
        val1 = m1[0].get("normalized_value_inr", 0) / 1e7
        val2 = m2[0].get("normalized_value_inr", 0) / 1e7
        growth = FinancialCalculator.calculate_yoy_growth(val1, val2)

        return {
            "metric": metric_name,
            "period_1": {"period": period1, "raw": m1[0].get("raw_value_str"), "source": m1[0].get("source_document_name")},
            "period_2": {"period": period2, "raw": m2[0].get("raw_value_str"), "source": m2[0].get("source_document_name")},
            "growth": growth
        }
