import os
import time
import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.models import (
    Document, DocumentChunk, DocumentPage, FinancialMetric,
    CrossDocConsistencyCheck, FinancialRisk, IPOReadinessScore,
    ProcessingStatus, MetricStatus
)
from app.schemas.schemas import DocumentResponse, DocumentChunkResponse
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.excel_parser import ExcelParser
from app.ingestion.csv_docx_parser import CSVDocxParser
from app.ingestion.chunking import FinancialChunker
from app.financial.metric_extractor import MetricExtractor
from app.financial.consistency_auditor import ConsistencyAuditor
from app.financial.risk_engine import RiskEngine
from app.financial.ipo_readiness_scorer import IPOReadinessScorer
from app.rag.embeddings import LocalEmbeddingEngine

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(company_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if company_id:
        query = query.filter(Document.company_id == company_id)
    docs = query.order_by(Document.id.desc()).all()
    results = []
    for d in docs:
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
        d_dict = {
            "id": d.id,
            "company_id": d.company_id,
            "filename": d.filename,
            "file_hash": d.file_hash,
            "document_type": d.document_type,
            "fiscal_year": d.fiscal_year,
            "page_count": d.page_count,
            "file_size_bytes": d.file_size_bytes,
            "processing_status": d.processing_status,
            "processing_duration_ms": d.processing_duration_ms,
            "error_message": d.error_message,
            "created_at": d.created_at,
            "chunk_count": chunk_count
        }
        results.append(d_dict)
    return results

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    company_id: int = Form(...),
    document_type: str = Form("Financial Filing"),
    fiscal_year: Optional[str] = Form("FY2024"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {settings.ALLOWED_EXTENSIONS}")

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # Check for duplicate document
    existing = db.query(Document).filter(
        Document.company_id == company_id,
        Document.file_hash == file_hash
    ).first()
    if existing:
        return existing

    # Save to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    dest_path = os.path.join(settings.UPLOAD_DIR, f"{company_id}_{file.filename}")
    with open(dest_path, "wb") as f:
        f.write(content)

    doc = Document(
        company_id=company_id,
        filename=file.filename,
        file_path=dest_path,
        file_hash=file_hash,
        document_type=document_type,
        fiscal_year=fiscal_year,
        file_size_bytes=len(content),
        processing_status=ProcessingStatus.PROCESSING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Ingestion Pipeline
    try:
        if ext == ".pdf":
            parsed = PDFParser.parse_pdf(dest_path)
        elif ext in [".xlsx", ".xls"]:
            parsed = ExcelParser.parse_excel(dest_path)
        elif ext == ".csv":
            parsed = CSVDocxParser.parse_csv(dest_path)
        elif ext == ".docx":
            parsed = CSVDocxParser.parse_docx(dest_path)
        else:
            raise ValueError(f"No parser for extension {ext}")

        doc.page_count = parsed.get("page_count", 1)
        doc.processing_status = ProcessingStatus.PARSED

        # Chunking & Embedding
        chunks = FinancialChunker.chunk_document(parsed, doc.id, doc.filename, doc.document_type)
        for ch in chunks:
            emb = LocalEmbeddingEngine.get_embedding(ch["chunk_text"])
            db_chunk = DocumentChunk(
                document_id=doc.id,
                page_number=ch.get("page_number"),
                section_title=ch.get("section_title"),
                chunk_index=ch.get("chunk_index"),
                chunk_text=ch.get("chunk_text"),
                embedding=emb,
                token_count=ch.get("token_count"),
                chunk_metadata=ch.get("chunk_metadata")
            )
            db.add(db_chunk)

        # Extract Metrics
        extracted = MetricExtractor.extract_metrics_from_text(parsed["full_text"], doc.filename)
        for m in extracted:
            m_obj = FinancialMetric(
                company_id=company_id,
                document_id=doc.id,
                metric_name=m["metric_name"],
                raw_value_str=m["raw_value_str"],
                normalized_value_inr=m["normalized_value_inr"],
                currency=m["currency"],
                unit=m["unit"],
                fiscal_year=m["fiscal_year"],
                statement_type=m["statement_type"],
                source_document_name=m["source_document_name"],
                source_page=m.get("source_page"),
                confidence_score=m["confidence_score"],
                status=MetricStatus.EXTRACTED
            )
            db.add(m_obj)

        doc.processing_status = ProcessingStatus.INDEXED
        doc.processing_duration_ms = int((time.time() - start_time) * 1000)
        db.commit()
        db.refresh(doc)

    except Exception as e:
        doc.processing_status = ProcessingStatus.FAILED
        doc.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Document parsing failed: {str(e)}")

    return doc

@router.get("/{document_id}/chunks", response_model=List[DocumentChunkResponse])
def get_document_chunks(document_id: int, db: Session = Depends(get_db)):
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
    return chunks

@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(doc.file_path, filename=doc.filename)
