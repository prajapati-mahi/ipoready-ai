import pytest
from app.guardrails.guardrails import FinancialGuardrail

def test_guardrails_low_confidence():
    fake_resp = {
        "answer": "Invented financial claim without proof",
        "confidence_score": 0.20,
        "calculations": []
    }
    audited = FinancialGuardrail.audit_response(fake_resp, [])
    assert audited["answer"] == "Not found in available documents."
    assert audited["guardrail_status"] == "PASSED_UNAVAILABLE_DATA"
