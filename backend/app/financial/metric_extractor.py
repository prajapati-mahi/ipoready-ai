import re
from typing import List, Dict, Any, Optional, Tuple

class MetricExtractor:
    CORE_METRICS = [
        "Revenue", "Revenue Growth", "Gross Profit", "Gross Margin",
        "EBITDA", "EBITDA Margin", "EBIT", "PAT", "PAT Margin",
        "Total Assets", "Total Liabilities", "Net Worth",
        "Total Debt", "Cash & Cash Equivalents", "Operating Cash Flow",
        "Free Cash Flow"
    ]

    UNIT_MULTIPLIERS = {
        "crore": 10_000_000,
        "cr": 10_000_000,
        "crores": 10_000_000,
        "lakh": 100_000,
        "lacs": 100_000,
        "lakhs": 100_000,
        "million": 1_000_000,
        "mn": 1_000_000,
        "billion": 1_000_000_000,
        "bn": 1_000_000_000,
        "thousand": 1_000,
        "k": 1_000
    }

    @classmethod
    def normalize_value(cls, raw_str: str, default_unit: str = "Crore") -> Tuple[float, str, str]:
        cleaned = raw_str.replace(",", "").replace("₹", "").replace("$", "").strip()
        match = re.search(r'([-\d.]+)\s*(cr|crore|crores|lakh|lakhs|lac|million|mn|billion|bn|thousand|k)?', cleaned, re.IGNORECASE)
        if not match:
            return 0.0, default_unit, raw_str

        try:
            num_part = float(match.group(1))
        except ValueError:
            return 0.0, default_unit, raw_str

        unit_part = match.group(2).lower() if match.group(2) else default_unit.lower()
        multiplier = cls.UNIT_MULTIPLIERS.get(unit_part, cls.UNIT_MULTIPLIERS.get(default_unit.lower(), 10_000_000))
        normalized = num_part * multiplier
        unit_display = "Crore" if "cr" in unit_part or "crore" in unit_part else "Lakh" if "lakh" in unit_part or "lac" in unit_part else unit_part.capitalize()

        return normalized, unit_display, raw_str

    @classmethod
    def extract_metrics_from_text(cls, text: str, doc_name: str, page_num: Optional[int] = None) -> List[Dict[str, Any]]:
        extracted = []
        patterns = [
            (r'(?:Total\s+)?Revenue(?:\s+from\s+Operations)?.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Revenue"),
            (r'EBITDA.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "EBITDA"),
            (r'(?:PAT|Profit\s+After\s+Tax|Net\s+Profit).*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "PAT"),
            (r'Gross\s+Profit.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Gross Profit"),
            (r'(?:Total\s+)?Debt.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Total Debt"),
            (r'(?:Operating\s+Cash\s+Flow|Cash\s+from\s+Operations).*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Operating Cash Flow"),
            (r'Net\s+Worth.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Net Worth"),
            (r'Total\s+Assets.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Total Assets"),
            (r'Total\s+Liabilities.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Total Liabilities"),
            (r'Cash\s+and\s+Cash\s+Equivalents.*?[:=]?\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr|Crore|Lakh|Mn)?', "Cash & Cash Equivalents")
        ]

        fy_match = re.search(r'(FY\s?20\d{2}|FY\s?\d{2}|20\d{2})', text, re.IGNORECASE)
        default_fy = fy_match.group(1).upper().replace(" ", "") if fy_match else "FY2024"

        for pattern, metric_name in patterns:
            try:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    val_str = match.group(1)
                    unit_str = match.group(2) if len(match.groups()) > 1 and match.group(2) else "Crore"
                    raw_combined = f"₹{val_str} {unit_str}"
                    normalized_val, unit_disp, _ = cls.normalize_value(raw_combined, unit_str)

                    extracted.append({
                        "metric_name": metric_name,
                        "raw_value_str": raw_combined,
                        "normalized_value_inr": normalized_val,
                        "currency": "INR",
                        "unit": unit_disp,
                        "fiscal_year": default_fy,
                        "statement_type": "P&L" if metric_name in ["Revenue", "EBITDA", "PAT", "Gross Profit"] else "Balance Sheet",
                        "source_document_name": doc_name,
                        "source_page": page_num,
                        "confidence_score": 0.94
                    })
            except Exception as e:
                print(f"Error extracting pattern {metric_name}: {e}")

        return extracted
