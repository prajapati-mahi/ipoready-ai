from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.demo.seeder import DemoSeeder
from app.schemas.schemas import CompanyResponse

router = APIRouter(prefix="/demo", tags=["Demo Management"])

@router.post("/seed", response_model=CompanyResponse)
def seed_demo(db: Session = Depends(get_db)):
    company = DemoSeeder.seed_demo_company(db, settings.UPLOAD_DIR)
    return company
