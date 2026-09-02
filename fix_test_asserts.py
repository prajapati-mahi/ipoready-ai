# -*- coding: utf-8 -*-
import os

backend_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\backend"

path_math = os.path.join(backend_root, "tests", "test_financial_math.py")
with open(path_math, "w", encoding="utf-8") as f:
    f.write('''import pytest
from app.financial.calculator import FinancialCalculator

def test_yoy_growth():
    res = FinancialCalculator.calculate_yoy_growth(100.0, 125.0)
    assert res["growth_pct"] == 25.0
    assert res["growth_amount"] == 25.0

def test_cagr():
    res = FinancialCalculator.calculate_cagr(78.0, 125.0, 2)
    assert round(res["cagr_pct"], 1) == 26.6
    assert res["years"] == 2

def test_margin():
    res = FinancialCalculator.calculate_margin(31.25, 125.0, "EBITDA Margin")
    assert res["margin_pct"] == 25.0

def test_ratio():
    res = FinancialCalculator.calculate_ratio(42.0, 85.0, "Debt to Equity")
    assert res["ratio"] == 0.49

def test_free_cash_flow():
    res = FinancialCalculator.calculate_free_cash_flow(27.20, 12.0)
    assert res["free_cash_flow"] == 15.20
''')

path_api = os.path.join(backend_root, "tests", "test_api_endpoints.py")
with open(path_api, "w", encoding="utf-8") as f:
    f.write('''import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["platform"] == "IPOReady AI"

def test_system_metrics_endpoint():
    response = client.get("/api/system/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["api_endpoints_count"] >= 20
    assert data["database_models_count"] >= 10
    assert data["evaluation_dataset_size"] >= 30

def test_demo_seed_endpoint():
    response = client.post("/api/demo/seed")
    assert response.status_code == 200
    assert response.json()["name"] == "Acme Technologies Private Limited"

def test_chat_analyst_endpoint():
    comp_res = client.get("/api/companies")
    assert comp_res.status_code == 200
    comp_id = comp_res.json()[0]["id"]

    chat_payload = {
        "company_id": comp_id,
        "query": "What was the revenue and EBITDA for FY2024?"
    }
    chat_res = client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert len(data["answer"]) > 5
    assert len(data["sources"]) >= 1
''')

print("Test assertions updated.")
