import pytest
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
