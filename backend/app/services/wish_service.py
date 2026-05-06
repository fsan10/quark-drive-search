from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models.wish import Wish, WishReply
from app.models.user import User
from app.models.resource import Resource
from app.schemas.wish import WishCreate, WishReplyCreate
from datetime import datetime


def create_wish(db: Session, data: WishCreate, user_id: int) -> dict:
    w = Wish(content=data.content, user_id=user_id)
    db.add(w)
    db.commit()
    db.refresh(w)
    return _wish_to_dict(w, db)


def get_user_wishes(db: Session, user_id: int) -> list[dict]:
    wishes = (
        db.query(Wish)
        .filter(Wish.user_id == user_id)
        .options(joinedload(Wish.replies).joinedload(WishReply.admin))
        .order_by(desc(Wish.created_at))
        .all()
    )
    return [_wish_to_dict(w, db) for w in wishes]


def get_all_wishes(db: Session, resolved: bool | None = None) -> list[dict]:
    query = db.query(Wish).options(joinedload(Wish.user), joinedload(Wish.replies))
    if resolved is not None:
        query = query.filter(Wish.is_resolved == resolved)
    wishes = query.order_by(desc(Wish.created_at)).all()
    return [_wish_to_dict(w, db) for w in wishes]


def reply_to_wish(db: Session, wish_id: int, data: WishReplyCreate, admin_id: int) -> dict | None:
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        return None

    reply = WishReply(
        wish_id=wish_id,
        content=data.content,
        resource_link=data.resource_link,
        resource_link_type=data.resource_link_type,
        resource_extraction_code=data.resource_extraction_code,
        resource_title=data.resource_title,
        replied_by=admin_id,
    )
    db.add(reply)

    if data.resource_link:
        resource = Resource(
            title=data.resource_title or "许愿资源",
            link=data.resource_link,
            link_type=data.resource_link_type or _detect_link_type(data.resource_link),
            extraction_code=data.resource_extraction_code,
            created_by=admin_id,
            is_visible=True,
        )
        db.add(resource)

    wish.is_resolved = True
    db.commit()
    db.refresh(reply)
    return _reply_to_dict(reply, db)


def get_unread_reply_count(db: Session, user_id: int) -> int:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return 0

    query = db.query(WishReply).join(Wish).filter(Wish.user_id == user_id)
    if user.wish_last_read_at:
        query = query.filter(WishReply.created_at > user.wish_last_read_at)
    return query.count()


def mark_replies_as_read(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.wish_last_read_at = datetime.utcnow()
        db.commit()


def get_user_replies(db: Session, user_id: int) -> list[dict]:
    replies = (
        db.query(WishReply)
        .join(Wish)
        .filter(Wish.user_id == user_id)
        .options(joinedload(WishReply.wish))
        .order_by(desc(WishReply.created_at))
        .all()
    )
    results = []
    for r in replies:
        results.append({
            "wish_id": r.wish_id,
            "wish_content": r.wish.content if r.wish else "",
            "reply_id": r.id,
            "reply_content": r.content,
            "resource_link": r.resource_link,
            "resource_link_type": r.resource_link_type,
            "resource_extraction_code": r.resource_extraction_code,
            "resource_title": r.resource_title,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return results


def delete_wish(db: Session, wish_id: int) -> bool:
    w = db.query(Wish).filter(Wish.id == wish_id).first()
    if not w:
        return False
    db.delete(w)
    db.commit()
    return True


def batch_delete_wishes(db: Session, ids: list[int]) -> dict:
    count = db.query(Wish).filter(Wish.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {"deleted_count": count}


def _detect_link_type(link: str) -> str:
    if "quark.cn" in link:
        return "quark"
    if "baidu.com" in link:
        return "baidu"
    if "aliyundrive.com" in link:
        return "alibaba"
    if "xunlei.com" in link:
        return "xunlei"
    if "123pan.com" in link:
        return "123pan"
    if "lanzou" in link:
        return "lanzou"
    return "other"


def _wish_to_dict(w: Wish, db: Session) -> dict:
    replies = w.replies if w.replies else []
    user = w.user if hasattr(w, 'user') and w.user else None
    if not user and w.user_id:
        user = db.query(User).filter(User.id == w.user_id).first()
    return {
        "id": w.id,
        "content": w.content,
        "user_id": w.user_id,
        "username": user.username if user else None,
        "is_resolved": w.is_resolved,
        "reply_count": len(replies),
        "replies": [_reply_to_dict(r, db) for r in replies],
        "created_at": w.created_at.isoformat() if w.created_at else None,
        "updated_at": w.updated_at.isoformat() if w.updated_at else None,
    }


def _reply_to_dict(r: WishReply, db: Session) -> dict:
    admin = r.admin if hasattr(r, 'admin') and r.admin else None
    if not admin and r.replied_by:
        admin = db.query(User).filter(User.id == r.replied_by).first()
    return {
        "id": r.id,
        "wish_id": r.wish_id,
        "content": r.content,
        "resource_link": r.resource_link,
        "resource_link_type": r.resource_link_type,
        "resource_extraction_code": r.resource_extraction_code,
        "resource_title": r.resource_title,
        "replied_by": r.replied_by,
        "admin_name": admin.username if admin else None,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
