from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate
from app.utils.security import verify_password
from app.config import get_settings


def _is_super_admin(user: User) -> bool:
    settings = get_settings()
    return user.username == settings.ADMIN_USERNAME and user.role == "super_admin"


def get_users(db: Session, page: int = 1, page_size: int = 20, role: str | None = None, is_active: bool | None = None) -> dict:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in items
        ],
    }


def check_edit_permission(db: Session, target_id: int, current_user: User) -> User:
    target = db.query(User).filter(User.id == target_id).first()
    if not target:
        raise ValueError("用户不存在")

    if _is_super_admin(target):
        raise ValueError("超级管理员账户不可修改")

    if target.is_admin_role and not _is_super_admin(current_user):
        raise ValueError("仅超级管理员可修改管理员账户")

    if target.id == current_user.id:
        raise ValueError("不能修改自己的账户")

    return target


def update_user(db: Session, user_id: int, data: UserUpdate, current_user: User | None = None) -> dict | None:
    if current_user:
        check_edit_permission(db, user_id, current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if "role" in update_data and update_data["role"] == "super_admin":
        raise ValueError("不能将用户设置为超级管理员")

    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def delete_user(db: Session, user_id: int, current_user: User) -> bool:
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        return False

    if _is_super_admin(target):
        raise ValueError("超级管理员账户不可删除")

    if target.is_admin_role and not _is_super_admin(current_user):
        raise ValueError("仅超级管理员可删除管理员账户")

    if target.id == current_user.id:
        raise ValueError("不能删除自己的账号")

    db.delete(target)
    db.commit()
    return True


def verify_current_admin_password(db: Session, admin_id: int, password: str) -> bool:
    admin = db.query(User).filter(User.id == admin_id).first()
    if not admin:
        return False
    return verify_password(password, admin.hashed_password)


def verify_user_password(db: Session, user_id: int, password: str) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    return verify_password(password, user.hashed_password)


def batch_delete_users(db: Session, ids: list[int], current_user: User) -> dict:
    settings = get_settings()
    super_admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    super_admin_id = super_admin.id if super_admin else -1

    if super_admin_id in ids:
        raise ValueError("超级管理员账户不可删除")

    if current_user.id in ids:
        raise ValueError("不能删除自己的账号")

    admin_ids = [uid for uid in ids if uid != super_admin_id and uid != current_user.id]
    if admin_ids:
        admin_users = db.query(User).filter(User.id.in_(admin_ids), User.role.in_(["admin", "super_admin"])).all()
        admin_user_ids = [u.id for u in admin_users]
        if admin_user_ids and not _is_super_admin(current_user):
            raise ValueError("仅超级管理员可删除管理员账户")

    users = db.query(User).filter(User.id.in_(ids)).all()
    count = 0
    for u in users:
        if u.id == super_admin_id or u.id == current_user.id:
            continue
        db.delete(u)
        count += 1
    db.commit()
    return {"deleted_count": count}
