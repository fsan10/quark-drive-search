from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from app.models.resource import Resource
from app.models.category import Category
from app.models.search_log import SearchLog


def search_resources(
    db: Session,
    keyword: str,
    page: int = 1,
    page_size: int = 20,
    link_type: str | None = None,
    category_id: int | None = None,
) -> dict:
    """搜索资源（前台公开接口，只返回可见资源）"""
    query = db.query(Resource).filter(Resource.is_visible == True)

    if keyword:
        query = query.filter(Resource.title.ilike(f"%{keyword}%"))
    if link_type:
        query = query.filter(Resource.link_type == link_type)
    if category_id:
        query = query.filter(Resource.category_id == category_id)

    total = query.count()
    items = (
        query.order_by(desc(Resource.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "link": r.link,
                "link_type": r.link_type,
                "extraction_code": r.extraction_code,
                "file_size": r.file_size,
                "category_id": r.category_id,
                "category_name": r.category.name if r.category else None,
                "view_count": r.view_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ],
    }


def log_search(db: Session, keyword: str, result_count: int, ip_address: str | None = None):
    """记录搜索日志"""
    log = SearchLog(keyword=keyword, result_count=result_count, ip_address=ip_address)
    db.add(log)
    db.commit()


def get_hot_searches(db: Session, limit: int = 10) -> list[str]:
    """获取热门搜索关键词"""
    results = (
        db.query(SearchLog.keyword, func.count(SearchLog.id).label("count"))
        .group_by(SearchLog.keyword)
        .order_by(text("count DESC"))
        .limit(limit)
        .all()
    )
    return [r.keyword for r in results]


def get_public_categories(db: Session) -> list[dict]:
    """获取前台分类列表（含资源数量）"""
    categories = db.query(Category).order_by(Category.sort_order).all()
    result = []
    for cat in categories:
        count = db.query(func.count(Resource.id)).filter(
            Resource.category_id == cat.id, Resource.is_visible == True
        ).scalar() or 0
        result.append({
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "resource_count": count,
        })
    return result
