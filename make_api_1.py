# -*- coding: utf-8 -*-
import os

app_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\backend\app"

def write_f(rel_path, code):
    p = os.path.join(app_root, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")
    print(f"Created: {rel_path}")

# 1. Auth API
write_f("api/auth.py", """
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.models import User, UserRole
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user = db.query(User).first()
    if not user:
        # Create default demo analyst user if none exists
        user = User(
            email="analyst@superjoin.ai",
            hashed_password=get_password_hash("superjoin2026"),
            full_name="Lead IPO Analyst",
            role=UserRole.ANALYST
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/token", response_model=Token)
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        # Seed default user for seamless demo login
        user = User(
            email=form_data.username or "analyst@superjoin.ai",
            hashed_password=get_password_hash(form_data.password or "superjoin2026"),
            full_name="Lead IPO Analyst",
            role=UserRole.ANALYST
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
""")

# 2. Companies API
write_f("api/companies.py", """
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Company, Document, FinancialMetric, FinancialRisk, IPOReadinessScore
from app.schemas.schemas import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=List[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    results = []
    for c in companies:
        doc_count = db.query(Document).filter(Document.company_id == c.id).count()
        metric_count = db.query(FinancialMetric).filter(FinancialMetric.company_id == c.id).count()
        risk_count = db.query(FinancialRisk).filter(FinancialRisk.company_id == c.id).count()
        latest_score = db.query(IPOReadinessScore).filter(IPOReadinessScore.company_id == c.id).order_by(IPOReadinessScore.id.desc()).first()
        
        c_dict = {
            "id": c.id,
            "name": c.name,
            "cin": c.cin,
            "sector": c.sector,
            "target_ipo_date": c.target_ipo_date,
            "description": c.description,
            "created_at": c.created_at,
            "document_count": doc_count,
            "metric_count": metric_count,
            "risk_count": risk_count,
            "readiness_score": latest_score.overall_score if latest_score else None
        }
        results.append(c_dict)
    return results

@router.post("", response_model=CompanyResponse)
def create_company(company_in: CompanyCreate, db: Session = Depends(get_db)):
    company = Company(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    doc_count = db.query(Document).filter(Document.company_id == company.id).count()
    metric_count = db.query(FinancialMetric).filter(FinancialMetric.company_id == company.id).count()
    risk_count = db.query(FinancialRisk).filter(FinancialRisk.company_id == company.id).count()
    latest_score = db.query(IPOReadinessScore).filter(IPOReadinessScore.company_id == company.id).order_by(IPOReadinessScore.id.desc()).first()

    return {
        "id": company.id,
        "name": company.name,
        "cin": company.cin,
        "sector": company.sector,
        "target_ipo_date": company.target_ipo_date,
        "description": company.description,
        "created_at": company.created_at,
        "document_count": doc_count,
        "metric_count": metric_count,
        "risk_count": risk_count,
        "readiness_score": latest_score.overall_score if latest_score else None
    }
""")

# 3. Documents API
write_f("api/documents.py", """
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
""")

print("Auth, Companies, and Documents APIs created.")
