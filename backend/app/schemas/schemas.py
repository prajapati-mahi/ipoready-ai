from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
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
    email: str
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
    guardrail_validation: Optional[Dict[str, Any]] = None
    final_output: Optional[str] = None
    latency_ms: int
    created_at: datetime

    class Config:
        from_attributes = True
