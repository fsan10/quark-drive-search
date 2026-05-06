from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from app.database import get_db
from app.models.resource import Resource
from app.models.user import User
from app.models.search_log import SearchLog
from app.utils.deps import get_current_admin
from app.models.user import User as UserModel

router = APIRouter(prefix="/api/admin/stats", tags=["统计"])


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    _admin: UserModel = Depends(get_current_admin),
):
    """获取概览统计数据"""
    total_resources = db.query(func.count(Resource.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_searches = db.query(func.count(SearchLog.id)).scalar() or 0

    today = datetime.utcnow().date()
    today_searches = db.query(func.count(SearchLog.id)).filter(
        cast(SearchLog.created_at, Date) == today
    ).scalar() or 0

    return {
        "total_resources": total_resources,
        "total_users": total_users,
        "total_searches": total_searches,
        "today_searches": today_searches,
    }
