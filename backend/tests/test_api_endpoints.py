import pytest
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
