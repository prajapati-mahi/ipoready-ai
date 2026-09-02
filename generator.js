const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, 'backend', 'app');

function writeFile(relPath, content) {
  const fullPath = path.join(root, relPath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, content.trim() + '\n', 'utf8');
  console.log('Wrote: ' + relPath);
}

// 1. Core Config
writeFile('core/config.py', `
import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "IPOReady AI - Intelligent IPO Readiness & Financial Document Analysis Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key-for-ipoready-ai-enterprise-portfolio-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/ipoready.db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    USE_DETERMINISTIC_REASONING: bool = True
    
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".xlsx", ".xls", ".csv", ".docx"]

    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()
`);

// 2. Core Database
writeFile('core/database.py', `
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

os.makedirs("./data", exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
`);

// 3. Core Security
writeFile('core/security.py', `
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
`);

// 4. Models
writeFile('models/models.py', `
from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime,
    ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    REVIEWER = "reviewer"

class ProcessingStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PARSED = "PARSED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class MetricStatus(str, enum.Enum):
    EXTRACTED = "EXTRACTED"
    VERIFIED = "VERIFIED"
    FLAGGED = "FLAGGED"
    REJECTED = "REJECTED"

class RiskSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ReviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ANALYST)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    cin = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=False)
    target_ipo_date = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    financial_metrics = relationship("FinancialMetric", back_populates="company", cascade="all, delete-orphan")
    risks = relationship("FinancialRisk", back_populates="company", cascade="all, delete-orphan")
    consistency_checks = relationship("CrossDocConsistencyCheck", back_populates="company", cascade="all, delete-orphan")
    readiness_scores = relationship("IPOReadinessScore", back_populates="company", cascade="all, delete-orphan")
    review_items = relationship("ReviewQueueItem", back_populates="company", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="company", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    document_type = Column(String(100), nullable=False)  # Annual Report, P&L, Balance Sheet, Investor Presentation, etc.
    fiscal_year = Column(String(50), nullable=True)
    page_count = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.UPLOADED)
    processing_duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    tables = relationship("DocumentTable", back_populates="document", cascade="all, delete-orphan")

class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)
    page_metadata = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="pages")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # Stored as float array JSON
    token_count = Column(Integer, default=0)
    chunk_metadata = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="chunks")

class DocumentTable(Base):
    __tablename__ = "document_tables"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    sheet_name = Column(String(100), nullable=True)
    table_title = Column(String(255), nullable=True)
    headers = Column(JSON, nullable=False)
    rows = Column(JSON, nullable=False)
    raw_csv = Column(Text, nullable=True)

    document = relationship("Document", back_populates="tables")

class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    metric_name = Column(String(100), nullable=False, index=True)
    raw_value_str = Column(String(100), nullable=False)
    normalized_value_inr = Column(Float, nullable=False)  # Normalized to INR Base (e.g. ?125 Cr = 1,250,000,000)
    currency = Column(String(10), default="INR")
    unit = Column(String(20), default="Crore")
    fiscal_year = Column(String(20), nullable=False, index=True)
    statement_type = Column(String(50), default="P&L")
    source_document_name = Column(String(255), nullable=False)
    source_page = Column(Integer, nullable=True)
    source_cell_ref = Column(String(50), nullable=True)  # e.g., Sheet P&L -> B12
    confidence_score = Column(Float, default=0.95)
    status = Column(Enum(MetricStatus), default=MetricStatus.EXTRACTED)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="financial_metrics")

class CrossDocConsistencyCheck(Base):
    __tablename__ = "cross_doc_consistency_checks"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    fiscal_year = Column(String(20), nullable=False)
    
    source_a_doc_name = Column(String(255), nullable=False)
    source_a_page_or_cell = Column(String(100), nullable=True)
    source_a_value_raw = Column(String(100), nullable=False)
    source_a_value_normalized = Column(Float, nullable=False)

    source_b_doc_name = Column(String(255), nullable=False)
    source_b_page_or_cell = Column(String(100), nullable=True)
    source_b_value_raw = Column(String(100), nullable=False)
    source_b_value_normalized = Column(Float, nullable=False)

    variance_amount = Column(Float, nullable=False)
    variance_percentage = Column(Float, nullable=False)
    severity = Column(Enum(RiskSeverity), default=RiskSeverity.MEDIUM)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="consistency_checks")

class FinancialRisk(Base):
    __tablename__ = "financial_risks"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    risk_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    severity = Column(Enum(RiskSeverity), default=RiskSeverity.HIGH)
    evidence = Column(Text, nullable=False)
    formula_used = Column(String(255), nullable=True)
    source_citation = Column(String(255), nullable=False)
    confidence_score = Column(Float, default=0.90)
    recommended_action = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="risks")

class IPOReadinessScore(Base):
    __tablename__ = "ipo_readiness_scores"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    overall_score = Column(Float, nullable=False)  # 0 - 100
    
    # 7 Pillar Breakdown
    financial_completeness_score = Column(Float, default=0.0)  # Max 20
    financial_consistency_score = Column(Float, default=0.0)   # Max 20
    profitability_score = Column(Float, default=0.0)           # Max 15
    cashflow_score = Column(Float, default=0.0)                # Max 15
    debt_health_score = Column(Float, default=0.0)             # Max 10
    growth_score = Column(Float, default=0.0)                  # Max 10
    document_coverage_score = Column(Float, default=0.0)       # Max 10

    breakdown_details = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="readiness_scores")

class ReviewQueueItem(Base):
    __tablename__ = "review_queue"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    item_type = Column(String(50), nullable=False)  # "METRIC", "CONSISTENCY", "RISK", "CALCULATION"
    reference_id = Column(Integer, nullable=True)
    reason = Column(String(255), nullable=False)
    original_payload = Column(JSON, nullable=False)
    modified_payload = Column(JSON, nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="review_items")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action_type = Column(String(100), nullable=False)  # "QUERY", "ANALYSIS", "EXTRACTION", "REVIEW"
    query_text = Column(Text, nullable=True)
    steps_executed = Column(JSON, nullable=False)
    retrieved_chunks = Column(JSON, nullable=True)
    tools_used = Column(JSON, nullable=True)
    calculations = Column(JSON, nullable=True)
    llm_output = Column(Text, nullable=True)
    guardrail_validation = Column(JSON, nullable=True)
    final_output = Column(Text, nullable=True)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)

    company = relationship("Company", back_populates="audit_logs")
`);

console.log('Models and Core generated successfully.');
