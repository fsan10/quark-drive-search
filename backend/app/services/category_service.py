from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.resource import Resource
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_categories(db: Session) -> list[dict]:
    """获取所有分类"""
    categories = db.query(Category).order_by(Category.sort_order).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "sort_order": c.sort_order,
            "created_by": c.created_by,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in categories
    ]


def create_category(db: Session, data: CategoryCreate, user_id: int) -> dict:
    """创建分类"""
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise ValueError("分类名称已存在")
    category = Category(**data.model_dump(), created_by=user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return _to_dict(category)


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> dict | None:
    """更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return _to_dict(category)


def delete_category(db: Session, category_id: int) -> bool:
    """删除分类（检查是否有关联资源）"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return False
    resource_count = db.query(Resource).filter(Resource.category_id == category_id).count()
    if resource_count > 0:
        raise ValueError(f"该分类下还有 {resource_count} 个资源，无法删除")
    db.delete(category)
    db.commit()
    return True


def _to_dict(c: Category) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "sort_order": c.sort_order,
        "created_by": c.created_by,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
