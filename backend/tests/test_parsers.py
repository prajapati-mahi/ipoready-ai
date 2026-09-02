import os
import pytest
from app.demo.generate_synthetic_docs import SyntheticDocumentGenerator
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.excel_parser import ExcelParser

@pytest.fixture(scope="session")
def sample_docs(tmp_path_factory):
    out_dir = str(tmp_path_factory.mktemp("data"))
    docs = SyntheticDocumentGenerator.generate_all(out_dir)
    return docs

def test_pdf_parser(sample_docs):
    pdf_path = [d for d in sample_docs if d.endswith("Annual_Report_FY24.pdf")][0]
    parsed = PDFParser.parse_pdf(pdf_path)
    assert parsed["page_count"] >= 1
    assert "ACME TECHNOLOGIES" in parsed["full_text"]
    assert len(parsed["tables"]) >= 1

def test_excel_parser(sample_docs):
    xlsx_path = [d for d in sample_docs if d.endswith("Financial_Model_FY22_FY24.xlsx")][0]
    parsed = ExcelParser.parse_excel(xlsx_path)
    assert parsed["sheet_count"] >= 2
    assert "P&L" in [s["sheet_name"] for s in parsed["sheets"]]
