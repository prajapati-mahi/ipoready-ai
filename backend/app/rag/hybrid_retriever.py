import re
from typing import List, Dict, Any, Optional
from app.rag.embeddings import LocalEmbeddingEngine

class HybridRetriever:
    @classmethod
    def retrieve(
        cls,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 5,
        fiscal_year_filter: Optional[str] = None,
        doc_type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not chunks:
            return []

        query_words = set(re.findall(r'\w+', query.lower()))
        query_vec = LocalEmbeddingEngine.get_embedding(query)

        scored_chunks = []

        for chunk in chunks:
            meta = chunk.get("chunk_metadata", {}) or {}
            chunk_fy = meta.get("fiscal_years", [])
            chunk_doc_type = meta.get("document_type", "")

            if fiscal_year_filter and chunk_fy and fiscal_year_filter not in chunk_fy:
                continue
            if doc_type_filter and doc_type_filter.lower() not in chunk_doc_type.lower():
                continue

            chunk_text = chunk.get("chunk_text", "")
            chunk_words = set(re.findall(r'\w+', chunk_text.lower()))
            
            overlap = len(query_words.intersection(chunk_words))
            keyword_score = overlap / max(1, len(query_words))

            chunk_vec = chunk.get("embedding")
            if not chunk_vec:
                chunk_vec = LocalEmbeddingEngine.get_embedding(chunk_text)
            vector_score = LocalEmbeddingEngine.cosine_similarity(query_vec, chunk_vec)

            combined_score = round((0.6 * vector_score) + (0.4 * keyword_score), 4)

            if any(word in chunk_text.lower() for word in ["fy24", "fy2024", "fy23", "fy2023", "cr", "crore"]):
                combined_score = min(1.0, combined_score + 0.1)

            scored_chunks.append({
                "chunk": chunk,
                "score": combined_score,
                "keyword_score": round(keyword_score, 4),
                "vector_score": vector_score,
                "source_document": meta.get("source_document", f"Doc {chunk.get('document_id')}"),
                "page": chunk.get("page_number") or meta.get("page"),
                "sheet": meta.get("sheet_name"),
                "snippet": chunk_text[:250] + ("..." if len(chunk_text) > 250 else "")
            })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]
