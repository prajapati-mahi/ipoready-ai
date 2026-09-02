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
                fy_matches = re.findall(r'(FYs?20d{2}|FYs?d{2}|20d{2}-d{2}|20d{2})', text, re.IGNORECASE)
                fiscal_years = list(set([f.upper().replace(" ", "") for f in fy_matches]))

                # Split page text into sentences/paragraphs
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
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
                table_text = f"FINANCIAL TABLE: {title}\n{header_str}\n" + "\n".join(row_strs)

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
