from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceBatchCreate
from app.services import resource_service, csv_service
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/resources", tags=["资源管理"])


class BatchDeleteRequest(BaseModel):
    ids: list[int]


class BatchVisibilityRequest(BaseModel):
    ids: list[int]
    is_visible: bool


@router.get("")
def list_resources(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    link_type: str | None = None,
    category_id: int | None = None,
    is_visible: bool | None = None,
    file_size_filter: str | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return resource_service.get_resources(
        db, page=page, page_size=page_size,
        keyword=keyword, link_type=link_type,
        category_id=category_id, is_visible=is_visible,
        file_size_filter=file_size_filter,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_resource(
    data: ResourceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return resource_service.create_resource(db, data, user_id=admin.id)


@router.put("/{resource_id}")
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = resource_service.update_resource(db, resource_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="资源不存在")
    return result


@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if not resource_service.delete_resource(db, resource_id):
        raise HTTPException(status_code=404, detail="资源不存在")
    return {"message": "删除成功"}


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def batch_create(
    data: ResourceBatchCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return resource_service.batch_create_resources(db, data, user_id=admin.id)


@router.post("/batch-delete")
def batch_delete(
    data: BatchDeleteRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if not data.ids:
        raise HTTPException(status_code=400, detail="请选择要删除的资源")
    result = resource_service.batch_delete_resources(db, data.ids)
    return {"message": f"成功删除 {result['deleted_count']} 个资源"}


@router.post("/batch-visibility")
def batch_visibility(
    data: BatchVisibilityRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    if not data.ids:
        raise HTTPException(status_code=400, detail="请选择要修改的资源")
    result = resource_service.batch_update_visibility(db, data.ids, data.is_visible)
    status_text = "可见" if data.is_visible else "隐藏"
    return {"message": f"成功将 {result['updated_count']} 个资源设为{status_text}"}


@router.put("/{resource_id}/visibility")
def toggle_visibility(
    resource_id: int,
    is_visible: bool = True,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = resource_service.update_resource(db, resource_id, ResourceUpdate(is_visible=is_visible))
    if not result:
        raise HTTPException(status_code=404, detail="资源不存在")
    return result


@router.post("/import/csv")
def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if not file.filename.endswith((".csv", ".CSV")):
        raise HTTPException(status_code=400, detail="仅支持CSV文件")
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
    return csv_service.import_csv(db, content, user_id=admin.id)
