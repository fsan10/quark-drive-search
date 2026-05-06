from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import donation_service

router = APIRouter(prefix="/api/donation", tags=["打赏"])


@router.get("")
def get_donation(db: Session = Depends(get_db)):
    return donation_service.get_donation_config(db)
