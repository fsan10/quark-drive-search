from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services import category_service
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/categories", tags=["分类管理"])


@router.get("")
def list_categories(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return category_service.get_categories(db)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return category_service.create_category(db, data, user_id=admin.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}")
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = category_service.update_category(db, category_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="分类不存在")
    return result


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    try:
        if not category_service.delete_category(db, category_id):
            raise HTTPException(status_code=404, detail="分类不存在")
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
