from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import announcement_service

router = APIRouter(prefix="/api/announcements", tags=["公告"])


@router.get("")
def list_announcements(db: Session = Depends(get_db)):
    return announcement_service.get_announcements(db, published_only=True)
