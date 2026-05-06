from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate
from app.services import announcement_service
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/announcements", tags=["公告管理"])


class BatchDeleteRequest(BaseModel):
    ids: list[int]


@router.get("")
def list_announcements(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return announcement_service.get_announcements(db)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return announcement_service.create_announcement(db, data, user_id=admin.id)


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = announcement_service.update_announcement(db, announcement_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="公告不存在")
    return result


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if not announcement_service.delete_announcement(db, announcement_id):
        raise HTTPException(status_code=404, detail="公告不存在")
    return {"message": "删除成功"}


@router.post("/batch-delete")
def batch_delete(
    data: BatchDeleteRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if not data.ids:
        raise HTTPException(status_code=400, detail="请选择要删除的公告")
    result = announcement_service.batch_delete_announcements(db, data.ids)
    return {"message": f"成功删除 {result['deleted_count']} 个公告"}
