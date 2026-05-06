from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wish import DonationConfigUpdate
from app.services import donation_service
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/donation", tags=["打赏配置"])


@router.get("")
def get_donation(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return donation_service.get_donation_config(db)


@router.put("")
def update_donation(
    data: DonationConfigUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return donation_service.update_donation_config(db, data.content, user_id=admin.id)
