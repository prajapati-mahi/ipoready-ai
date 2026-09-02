from typing import Dict, Any, List

class FinancialGuardrail:
    @staticmethod
    def audit_response(response_dict: Dict[str, Any], raw_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        confidence = response_dict.get("confidence_score", 0.0)

        if confidence < 0.35:
            response_dict["answer"] = "Not found in available documents."
            response_dict["guardrail_status"] = "PASSED_UNAVAILABLE_DATA"
            return response_dict

        calculations = response_dict.get("calculations", [])
        for calc in calculations:
            if "error" in calc:
                response_dict["guardrail_status"] = "FLAGGED_MATH_ERROR"
                response_dict["answer"] += "\n\n*Warning: Calculation error detected in math validation step.*"

        response_dict["guardrail_status"] = "PASSED"
        return response_dict
