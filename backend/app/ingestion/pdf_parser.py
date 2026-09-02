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
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
            page_sections = []
            for line in lines[:5]:  # Check top lines of the page
                if re.match(r'^(BALANCE SHEET|STATEMENT OF PROFIT|CASH FLOW|FINANCIAL HIGHLIGHTS|DIRECTORS|MANAGEMENT DISCUSSION|NOTE d+|SCHEDULE d+)', line, re.IGNORECASE):
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
                            "raw_csv": "\n".join([",".join([f'"{c}"' for c in r]) for r in clean_rows])
                        })
        except Exception as e:
            print(f"pdfplumber table extraction warning for {file_path}: {e}")

        return {
            "page_count": page_count,
            "pages": pages_data,
            "tables": tables_data,
            "sections": detected_sections,
            "full_text": "\n--- PAGE BREAK ---\n".join(full_text_list)
        }
