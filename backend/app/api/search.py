from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import search_service

router = APIRouter(prefix="/api/search", tags=["搜索"])


@router.get("")
def search(
    keyword: str = Query("", description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    link_type: str | None = Query(None),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
    request: Request = None,
):
    if not keyword and not link_type and not category_id:
        return {"total": 0, "page": page, "page_size": page_size, "items": []}

    results = search_service.search_resources(
        db, keyword=keyword, page=page, page_size=page_size,
        link_type=link_type, category_id=category_id,
    )
    if keyword:
        client_ip = request.client.host if request else None
        search_service.log_search(db, keyword=keyword, result_count=results["total"], ip_address=client_ip)
    return results


@router.get("/hot")
def hot_searches(db: Session = Depends(get_db)):
    return search_service.get_hot_searches(db)


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return search_service.get_public_categories(db)
