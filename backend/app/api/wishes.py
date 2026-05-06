from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wish import WishCreate
from app.services import wish_service
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/wishes", tags=["许愿池"])


@router.post("")
def create_wish(
    data: WishCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return wish_service.create_wish(db, data, user_id=user.id)


@router.get("/my")
def my_wishes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return wish_service.get_user_wishes(db, user_id=user.id)


@router.get("/replies")
def my_replies(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return wish_service.get_user_replies(db, user_id=user.id)


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    count = wish_service.get_unread_reply_count(db, user_id=user.id)
    return {"count": count}


@router.post("/mark-read")
def mark_read(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    wish_service.mark_replies_as_read(db, user_id=user.id)
    return {"message": "ok"}
