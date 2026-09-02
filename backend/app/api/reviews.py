from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import ReviewQueueItem, ReviewStatus
from app.schemas.schemas import ReviewQueueResponse, ReviewActionRequest

router = APIRouter(prefix="/reviews", tags=["Human Review Queue"])

@router.get("", response_model=List[ReviewQueueResponse])
def list_review_items(company_id: int, db: Session = Depends(get_db)):
    items = db.query(ReviewQueueItem).filter(ReviewQueueItem.company_id == company_id).order_by(ReviewQueueItem.id.desc()).all()
    return items

@router.post("/{item_id}/action", response_model=ReviewQueueResponse)
def process_review_action(item_id: int, action_in: ReviewActionRequest, db: Session = Depends(get_db)):
    item = db.query(ReviewQueueItem).filter(ReviewQueueItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")
    
    item.review_status = action_in.action
    item.notes = action_in.notes
    if action_in.modified_payload:
        item.modified_payload = action_in.modified_payload
    item.reviewed_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(item)
    return item
