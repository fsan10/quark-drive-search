from fastapi import APIRouter, Depends
from app.config import get_settings
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/models", tags=["模型管理"])


@router.get("/available")
def get_available_models(_admin: User = Depends(get_current_admin)):
    """获取可用的AI模型列表"""
    settings = get_settings()
    return {
        "models": settings.available_models,
        "current": settings.AI_MODEL,
    }
