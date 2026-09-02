from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import AuditLog
from app.schemas.schemas import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(company_id: int, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).filter(AuditLog.company_id == company_id).order_by(AuditLog.id.desc()).limit(50).all()
    return logs
