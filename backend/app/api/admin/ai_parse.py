from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.resource import AiParseRequest, AiParseResponse, AiBatchParseResponse
from app.services import ai_service
from app.utils.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/api/admin/ai", tags=["AI识别"])


@router.post("/parse", response_model=AiParseResponse)
def ai_parse(
    data: AiParseRequest,
    _db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """AI识别单条分享文本（仅预览，不入库）"""
    parsed = ai_service.parse_share_text(data.text, model=data.model)
    return AiParseResponse(parsed=parsed)


@router.post("/parse-batch", response_model=AiBatchParseResponse)
def ai_batch_parse(
    data: AiParseRequest,
    _db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """AI批量识别分享文本（仅预览，不入库）"""
    return ai_service.batch_parse_share_text(data.text, model=data.model)


@router.post("/parse-and-save")
def ai_parse_and_save(
    data: AiParseRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """AI识别并直接入库（一键导入）"""
    return ai_service.ai_parse_and_save(data.text, user_id=admin.id, db=db, model=data.model)
