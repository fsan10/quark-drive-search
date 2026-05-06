from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wish import WishReplyCreate
from app.services import wish_service
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/wishes", tags=["许愿池管理"])


class BatchDeleteRequest(BaseModel):
    ids: list[int]


@router.get("")
def list_wishes(
    resolved: bool | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return wish_service.get_all_wishes(db, resolved=resolved)


@router.post("/{wish_id}/reply")
def reply_wish(
    wish_id: int,
    data: WishReplyCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = wish_service.reply_to_wish(db, wish_id, data, admin_id=admin.id)
    if not result:
        raise HTTPException(status_code=404, detail="许愿不存在")
    return result


@router.delete("/{wish_id}")
def delete_wish(
    wish_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if not wish_service.delete_wish(db, wish_id):
        raise HTTPException(status_code=404, detail="许愿不存在")
    return {"message": "删除成功"}


@router.post("/batch-delete")
def batch_delete(
    data: BatchDeleteRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if not data.ids:
        raise HTTPException(status_code=400, detail="请选择要删除的许愿")
    result = wish_service.batch_delete_wishes(db, data.ids)
    return {"message": f"成功删除 {result['deleted_count']} 个许愿"}
