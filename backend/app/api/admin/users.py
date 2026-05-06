from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserUpdate
from app.services import user_service
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/users", tags=["用户管理"])


class BatchDeleteRequest(BaseModel):
    ids: list[int]


class VerifyPasswordRequest(BaseModel):
    password: str


@router.get("")
def list_users(
    page: int = 1,
    page_size: int = 20,
    role: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = user_service.get_users(db, page=page, page_size=page_size, role=role, is_active=is_active)
    result["current_admin_role"] = admin.role
    result["current_admin_id"] = admin.id
    return result


@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        result = user_service.update_user(db, user_id, data, current_user=admin)
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        if not user_service.delete_user(db, user_id, current_user=admin):
            raise HTTPException(status_code=404, detail="用户不存在")
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-current-password")
def verify_current_password(
    data: VerifyPasswordRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if user_service.verify_current_admin_password(db, admin.id, data.password):
        return {"valid": True}
    raise HTTPException(status_code=400, detail="密码验证失败")


@router.post("/{user_id}/verify-password")
def verify_user_password(
    user_id: int,
    data: VerifyPasswordRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if user_service.verify_user_password(db, user_id, data.password):
        return {"valid": True}
    raise HTTPException(status_code=400, detail="密码验证失败")


@router.post("/batch-delete")
def batch_delete(
    data: BatchDeleteRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if not data.ids:
        raise HTTPException(status_code=400, detail="请选择要删除的用户")
    try:
        result = user_service.batch_delete_users(db, data.ids, current_user=admin)
        return {"message": f"成功删除 {result['deleted_count']} 个用户"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
