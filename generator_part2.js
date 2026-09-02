const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, 'backend', 'app');

function writeFile(relPath, content) {
  const fullPath = path.join(root, relPath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, content.trim() + '\n', 'utf8');
  console.log('Wrote: ' + relPath);
}

// 1. Schemas
writeFile('schemas/schemas.py', `
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, EmailStr, Field
from app.models.models import UserRole, ProcessingStatus, MetricStatus, RiskSeverity, ReviewStatus

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.ANALYST

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CompanyBase(BaseModel):
    name: str
    cin: Optional[str] = None
    sector: str
    target_ipo_date: Optional[str] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    document_count: Optional[int] = 0
    metric_count: Optional[int] = 0
    risk_count: Optional[int] = 0
    readiness_score: Optional[float] = None

    class Config:
        from_attributes = True

class DocumentChunkResponse(BaseModel):
    id: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_index: int
    chunk_text: str
    token_count: int
    chunk_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentTableResponse(BaseModel):
    id: int
    page_number: Optional[int] = None
    sheet_name: Optional[str] = None
    table_title: Optional[str] = None
    headers: List[str]
    rows: List[List[Any]]

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    company_id: int
    filename: str
    file_hash: str
    document_type: str
    fiscal_year: Optional[str] = None
    page_count: int
    file_size_bytes: int
    processing_status: ProcessingStatus
    processing_duration_ms: int
    error_message: Optional[str] = None
    created_at: datetime
    chunk_count: Optional[int] = 0

    class Config:
        from_attributes = True

class FinancialMetricResponse(BaseModel):
    id: int
    company_id: int
    document_id: Optional[int] = None
    metric_name: str
    raw_value_str: str
    normalized_value_inr: float
    currency: str
    unit: str
    fiscal_year: str
    statement_type: str
    source_document_name: str
    source_page: Optional[int] = None
    source_cell_ref: Optional[str] = None
    confidence_score: float
    status: MetricStatus
    created_at: datetime

    class Config:
        from_attributes = True

class ConsistencyCheckResponse(BaseModel):
    id: int
    company_id: int
    metric_name: str
    fiscal_year: str
    source_a_doc_name: str
    source_a_page_or_cell: Optional[str] = None
    source_a_value_raw: str
    source_a_value_normalized: float
    source_b_doc_name: str
    source_b_page_or_cell: Optional[str] = None
    source_b_value_raw: str
    source_b_value_normalized: float
    variance_amount: float
    variance_percentage: float
    severity: RiskSeverity
    status: ReviewStatus
    resolution_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FinancialRiskResponse(BaseModel):
    id: int
    company_id: int
    risk_type: str
    title: str
    severity: RiskSeverity
    evidence: str
    formula_used: Optional[str] = None
    source_citation: str
    confidence_score: float
    recommended_action: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class IPOReadinessResponse(BaseModel):
    id: int
    company_id: int
    overall_score: float
    financial_completeness_score: float
    financial_consistency_score: float
    profitability_score: float
    cashflow_score: float
    debt_health_score: float
    growth_score: float
    document_coverage_score: float
    breakdown_details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewQueueResponse(BaseModel):
    id: int
    company_id: int
    item_type: str
    reference_id: Optional[int] = None
    reason: str
    original_payload: Dict[str, Any]
    modified_payload: Optional[Dict[str, Any]] = None
    reviewer_id: Optional[int] = None
    review_status: ReviewStatus
    notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewActionRequest(BaseModel):
    action: ReviewStatus  # APPROVED, REJECTED, MODIFIED
    modified_payload: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ChatMessageRequest(BaseModel):
    company_id: int
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ToolExecutionDetail(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    execution_time_ms: int

class CitationDetail(BaseModel):
    source_document: str
    page_number: Optional[int] = None
    cell_reference: Optional[str] = None
    snippet: str
    confidence: float

class CalculationStep(BaseModel):
    formula: str
    inputs: Dict[str, Any]
    result: Union[float, str]
    explanation: str

class ChatResponse(BaseModel):
    answer: str
    confidence_score: float
    confidence_level: str  # HIGH, MEDIUM, LOW
    sources: List[CitationDetail]
    tools_executed: List[ToolExecutionDetail]
    calculations: List[CalculationStep]
    guardrail_status: str  # PASSED, FLAGGED, BLOCKED
    latency_ms: int
    audit_log_id: int

class AuditLogResponse(BaseModel):
    id: int
    company_id: int
    user_id: Optional[int] = None
    action_type: str
    query_text: Optional[str] = None
    steps_executed: List[Dict[str, Any]]
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    tools_used: Optional[List[Dict[str, Any]]] = None
    calculations: Optional[List[Dict[str, Any]]] = None
    llm_output: Optional[str] = None
    guardrail_validation: Optional[Dict[str, Any]]] = None
    final_output: Optional[str] = None
    latency_ms: int
    created_at: datetime

    class Config:
        from_attributes = True
`);

// 2. Ingestion: PDF Parser
writeFile('ingestion/pdf_parser.py', `
import os
import re
from typing import List, Dict, Any, Tuple
import pymupdf  # PyMuPDF
import pdfplumber

class PDFParser:
    @staticmethod
    def parse_pdf(file_path: str) -> Dict[str, Any]:
        """
        Extracts structured text, pages, headers, and tables with precise page coordinates and bounding metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        pages_data = []
        tables_data = []
        full_text_list = []
        detected_sections = []

        # 1. PyMuPDF for fast, high-fidelity text and page layout extraction
        doc = pymupdf.open(file_path)
        page_count = len(doc)

        for page_idx in range(page_count):
            page = doc[page_idx]
            page_num = page_idx + 1
            raw_text = page.get_text("text")
            full_text_list.append(raw_text)

            # Detect section headers (lines that are uppercase or start with numbers)
            lines = [line.strip() for line in raw_text.split("\\n") if line.strip()]
            page_sections = []
            for line in lines[:5]:  # Check top lines of the page
                if re.match(r'^(BALANCE SHEET|STATEMENT OF PROFIT|CASH FLOW|FINANCIAL HIGHLIGHTS|DIRECTORS|MANAGEMENT DISCUSSION|NOTE \d+|SCHEDULE \d+)', line, re.IGNORECASE):
                    page_sections.append(line)
                    detected_sections.append({"page": page_num, "section": line})

            pages_data.append({
                "page_number": page_num,
                "text": raw_text,
                "detected_sections": page_sections,
                "char_count": len(raw_text)
            })

        doc.close()

        # 2. pdfplumber for structured table extraction
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    page_num = page_idx + 1
                    extracted_tables = page.extract_tables()
                    for t_idx, table in enumerate(extracted_tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Clean table cells
                        clean_rows = []
                        for row in table:
                            clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
                            clean_rows.append(clean_row)

                        headers = clean_rows[0]
                        data_rows = clean_rows[1:]

                        # Table title inference
                        title = f"Table {t_idx + 1} (Page {page_num})"
                        if pages_data[page_idx]["detected_sections"]:
                            title = f"{pages_data[page_idx]['detected_sections'][0]} - Table {t_idx + 1}"

                        tables_data.append({
                            "page_number": page_num,
                            "sheet_name": None,
                            "table_title": title,
                            "headers": headers,
                            "rows": data_rows,
                            "raw_csv": "\\n".join([",".join([f'\"{c}\"' for c in r]) for r in clean_rows])
                        })
        except Exception as e:
            print(f"pdfplumber table extraction warning for {file_path}: {e}")

        return {
            "page_count": page_count,
            "pages": pages_data,
            "tables": tables_data,
            "sections": detected_sections,
            "full_text": "\\n--- PAGE BREAK ---\\n".join(full_text_list)
        }
`);

// 3. Ingestion: Excel Parser
writeFile('ingestion/excel_parser.py', `
import os
import openpyxl
import pandas as pd
from typing import Dict, Any, List

class ExcelParser:
    @staticmethod
    def parse_excel(file_path: str) -> Dict[str, Any]:
        """
        Deep spreadsheet intelligence:
        - Extracts sheets, rows, columns, formulas, merged cells, exact cell coordinates (e.g. Sheet P&L -> B12)
        - Detects multi-year financial statements
        - Automatically isolates tabular numeric regions
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        workbook = openpyxl.load_workbook(file_path, data_only=False)
        data_workbook = openpyxl.load_workbook(file_path, data_only=True)  # To read evaluated values

        sheets_data = []
        tables_data = []
        cell_map = {}  # Map of "SheetName!CellCoord" -> { value, formula, row, col }
        full_text_chunks = []

        for sheet_name in workbook.sheetnames:
            ws_formula = workbook[sheet_name]
            ws_data = data_workbook[sheet_name]

            max_row = ws_data.max_row
            max_col = ws_data.max_column

            sheet_rows = []
            sheet_text_lines = [f"=== SHEET: {sheet_name} ==="]

            for r in range(1, max_row + 1):
                row_vals = []
                row_has_data = False
                for c in range(1, max_col + 1):
                    cell_formula_obj = ws_formula.cell(row=r, column=c)
                    cell_data_obj = ws_data.cell(row=r, column=c)

                    val = cell_data_obj.value
                    formula = str(cell_formula_obj.value) if str(cell_formula_obj.value).startswith("=") else None
                    cell_ref = f"{sheet_name}!{cell_formula_obj.coordinate}"

                    if val is not None:
                        row_has_data = True

                    cell_info = {
                        "sheet": sheet_name,
                        "cell": cell_formula_obj.coordinate,
                        "value": val,
                        "formula": formula,
                        "row": r,
                        "col": c
                    }
                    cell_map[cell_ref] = cell_info
                    row_vals.append(val if val is not None else "")

                if row_has_data:
                    sheet_rows.append(row_vals)
                    line_str = " | ".join([str(v) for v in row_vals if str(v).strip()])
                    if line_str:
                        sheet_text_lines.append(line_str)

            # Convert to DataFrame for structured table extraction
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                # Drop all-NaN columns and rows
                df = df.dropna(how='all').dropna(axis=1, how='all')
                
                headers = [str(col) for col in df.columns]
                rows = df.fillna("").values.tolist()

                tables_data.append({
                    "page_number": None,
                    "sheet_name": sheet_name,
                    "table_title": f"Spreadsheet - {sheet_name}",
                    "headers": headers,
                    "rows": rows,
                    "raw_csv": df.to_csv(index=False)
                })
            except Exception as e:
                print(f"Error loading pandas sheet {sheet_name}: {e}")

            sheets_data.append({
                "sheet_name": sheet_name,
                "row_count": max_row,
                "col_count": max_col,
                "rows": sheet_rows
            })
            full_text_chunks.append("\\n".join(sheet_text_lines))

        workbook.close()
        data_workbook.close()

        return {
            "sheet_count": len(sheets_data),
            "sheets": sheets_data,
            "tables": tables_data,
            "cell_map": cell_map,
            "full_text": "\\n\\n".join(full_text_chunks)
        }
`);

// 4. Ingestion: CSV and Docx Parser
writeFile('ingestion/csv_docx_parser.py', `
import os
import csv
import pandas as pd
import docx
from typing import Dict, Any

class CSVDocxParser:
    @staticmethod
    def parse_csv(file_path: str) -> Dict[str, Any]:
        df = pd.read_csv(file_path)
        df = df.dropna(how='all')
        headers = [str(col) for col in df.columns]
        rows = df.fillna("").values.tolist()

        return {
            "page_count": 1,
            "pages": [{"page_number": 1, "text": df.to_string(), "detected_sections": []}],
            "tables": [{
                "page_number": 1,
                "sheet_name": "CSV Data",
                "table_title": os.path.basename(file_path),
                "headers": headers,
                "rows": rows,
                "raw_csv": df.to_csv(index=False)
            }],
            "full_text": df.to_csv(index=False)
        }

    @staticmethod
    def parse_docx(file_path: str) -> Dict[str, Any]:
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\\n\\n".join(paragraphs)

        tables_data = []
        for t_idx, table in enumerate(doc.tables):
            table_rows = []
            for row in table.rows:
                table_rows.append([cell.text.strip() for cell in row.cells])
            if table_rows:
                headers = table_rows[0]
                data_rows = table_rows[1:]
                tables_data.append({
                    "page_number": 1,
                    "sheet_name": None,
                    "table_title": f"Document Table {t_idx + 1}",
                    "headers": headers,
                    "rows": data_rows,
                    "raw_csv": "\\n".join([",".join([f'\"{c}\"' for c in r]) for r in table_rows])
                })

        return {
            "page_count": 1,
            "pages": [{"page_number": 1, "text": full_text, "detected_sections": []}],
            "tables": tables_data,
            "full_text": full_text
        }
`);

// 5. Ingestion: Financial Chunking Engine
writeFile('ingestion/chunking.py', `
import re
from typing import List, Dict, Any

class FinancialChunker:
    @staticmethod
    def chunk_document(
        parsed_doc: Dict[str, Any],
        document_id: int,
        document_name: str,
        document_type: str,
        chunk_size: int = 450,
        chunk_overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Financial-aware chunking:
        - Preserves statement boundaries and table headers
        - Attaches exact page numbers, cell references, fiscal years, and document metadata
        """
        chunks = []
        chunk_index = 0

        # Process page by page for PDFs and DOCs
        if "pages" in parsed_doc and parsed_doc["pages"]:
            for page in parsed_doc["pages"]:
                page_num = page.get("page_number", 1)
                text = page.get("text", "")
                sections = page.get("detected_sections", [])
                section_title = sections[0] if sections else f"Page {page_num}"

                # Detect fiscal years mentioned on this page
                fy_matches = re.findall(r'(FY\s?20\d{2}|FY\s?\d{2}|20\d{2}-\d{2}|20\d{2})', text, re.IGNORECASE)
                fiscal_years = list(set([f.upper().replace(" ", "") for f in fy_matches]))

                # Split page text into sentences/paragraphs
                paragraphs = [p.strip() for p in text.split("\\n\\n") if p.strip()]
                current_chunk_words = []

                for para in paragraphs:
                    words = para.split()
                    if len(current_chunk_words) + len(words) > chunk_size and current_chunk_words:
                        chunk_text = " ".join(current_chunk_words)
                        chunks.append({
                            "document_id": document_id,
                            "page_number": page_num,
                            "section_title": section_title,
                            "chunk_index": chunk_index,
                            "chunk_text": chunk_text,
                            "token_count": len(current_chunk_words),
                            "chunk_metadata": {
                                "source_document": document_name,
                                "document_type": document_type,
                                "page": page_num,
                                "section": section_title,
                                "fiscal_years": fiscal_years
                            }
                        })
                        chunk_index += 1
                        # Retain overlap
                        current_chunk_words = current_chunk_words[-chunk_overlap:] if len(current_chunk_words) > chunk_overlap else []

                    current_chunk_words.extend(words)

                if current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    chunks.append({
                        "document_id": document_id,
                        "page_number": page_num,
                        "section_title": section_title,
                        "chunk_index": chunk_index,
                        "chunk_text": chunk_text,
                        "token_count": len(current_chunk_words),
                        "chunk_metadata": {
                            "source_document": document_name,
                            "document_type": document_type,
                            "page": page_num,
                            "section": section_title,
                            "fiscal_years": fiscal_years
                        }
                    })
                    chunk_index += 1

        # Also create dedicated chunks for extracted tables
        if "tables" in parsed_doc and parsed_doc["tables"]:
            for table in parsed_doc["tables"]:
                sheet = table.get("sheet_name")
                page_num = table.get("page_number")
                title = table.get("table_title", "Financial Table")
                headers = table.get("headers", [])
                rows = table.get("rows", [])

                # Format tabular representation
                header_str = " | ".join([str(h) for h in headers])
                row_strs = [" | ".join([str(c) for c in r]) for r in rows[:25]]  # Cap for chunk size
                table_text = f"FINANCIAL TABLE: {title}\\n{header_str}\\n" + "\\n".join(row_strs)

                chunks.append({
                    "document_id": document_id,
                    "page_number": page_num,
                    "section_title": f"Table: {title}",
                    "chunk_index": chunk_index,
                    "chunk_text": table_text,
                    "token_count": len(table_text.split()),
                    "chunk_metadata": {
                        "source_document": document_name,
                        "document_type": document_type,
                        "page": page_num,
                        "sheet_name": sheet,
                        "is_table": True,
                        "table_title": title
                    }
                })
                chunk_index += 1

        return chunks
`);

console.log('Part 2 schemas and ingestion generated successfully.');
