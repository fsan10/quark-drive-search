from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate


def get_announcements(db: Session, published_only: bool = False) -> list[dict]:
    query = db.query(Announcement)
    if published_only:
        query = query.filter(Announcement.is_published == True)
    items = query.order_by(Announcement.sort_order, desc(Announcement.created_at)).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "is_published": a.is_published,
            "sort_order": a.sort_order,
            "created_by": a.created_by,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
        }
        for a in items
    ]


def create_announcement(db: Session, data: AnnouncementCreate, user_id: int) -> dict:
    a = Announcement(**data.model_dump(), created_by=user_id)
    db.add(a)
    db.commit()
    db.refresh(a)
    return _to_dict(a)


def update_announcement(db: Session, announcement_id: int, data: AnnouncementUpdate) -> dict | None:
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(a, key, value)
    db.commit()
    db.refresh(a)
    return _to_dict(a)


def delete_announcement(db: Session, announcement_id: int) -> bool:
    a = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not a:
        return False
    db.delete(a)
    db.commit()
    return True


def batch_delete_announcements(db: Session, ids: list[int]) -> dict:
    count = db.query(Announcement).filter(Announcement.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {"deleted_count": count}


def _to_dict(a: Announcement) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "content": a.content,
        "is_published": a.is_published,
        "sort_order": a.sort_order,
        "created_by": a.created_by,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }
