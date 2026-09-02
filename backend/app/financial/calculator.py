from typing import Dict, Any

class FinancialCalculator:
    @staticmethod
    def calculate_yoy_growth(initial_val: float, final_val: float) -> Dict[str, Any]:
        if initial_val == 0:
            return {"growth_pct": None, "formula": "((final - initial) / initial) * 100", "error": "Division by zero"}
        growth_pct = round(((final_val - initial_val) / abs(initial_val)) * 100, 2)
        return {
            "initial_value": initial_val,
            "final_value": final_val,
            "growth_pct": growth_pct,
            "growth_amount": round(final_val - initial_val, 2),
            "formula": f"(({final_val} - {initial_val}) / {abs(initial_val)}) * 100 = {growth_pct}%"
        }

    @staticmethod
    def calculate_cagr(initial_val: float, final_val: float, years: int) -> Dict[str, Any]:
        if initial_val <= 0 or final_val <= 0 or years <= 0:
            return {"cagr_pct": None, "formula": "(final/initial)^(1/n) - 1", "error": "Invalid values for CAGR"}
        cagr = (pow(final_val / initial_val, 1.0 / years) - 1.0) * 100.0
        cagr_pct = round(cagr, 2)
        return {
            "initial_value": initial_val,
            "final_value": final_val,
            "years": years,
            "cagr_pct": cagr_pct,
            "formula": f"({final_val} / {initial_val})^(1/{years}) - 1 = {cagr_pct}%"
        }

    @staticmethod
    def calculate_margin(metric_val: float, revenue: float, metric_name: str = "EBITDA") -> Dict[str, Any]:
        if revenue == 0:
            return {"margin_pct": None, "formula": "(metric / revenue) * 100", "error": "Revenue is zero"}
        margin_pct = round((metric_val / revenue) * 100.0, 2)
        return {
            "metric_name": metric_name,
            "metric_value": metric_val,
            "revenue": revenue,
            "margin_pct": margin_pct,
            "formula": f"({metric_val} / {revenue}) * 100 = {margin_pct}%"
        }

    @staticmethod
    def calculate_ratio(numerator: float, denominator: float, ratio_name: str = "Debt to Equity") -> Dict[str, Any]:
        if denominator == 0:
            return {"ratio": None, "formula": "numerator / denominator", "error": "Denominator is zero"}
        ratio = round(numerator / denominator, 2)
        return {
            "ratio_name": ratio_name,
            "numerator": numerator,
            "denominator": denominator,
            "ratio": ratio,
            "formula": f"{numerator} / {denominator} = {ratio}x"
        }

    @staticmethod
    def calculate_free_cash_flow(operating_cash_flow: float, capital_expenditure: float) -> Dict[str, Any]:
        fcf = round(operating_cash_flow - capital_expenditure, 2)
        return {
            "operating_cash_flow": operating_cash_flow,
            "capital_expenditure": capital_expenditure,
            "free_cash_flow": fcf,
            "formula": f"{operating_cash_flow} - {capital_expenditure} = {fcf}"
        }
