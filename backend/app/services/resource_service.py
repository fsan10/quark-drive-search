import re
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.resource import Resource
from app.models.category import Category
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceBatchCreate


def _parse_size_to_mb(size_str: str) -> float | None:
    if not size_str:
        return None
    size_str = size_str.strip().upper()
    match = re.match(r'^([\d.]+)\s*(KB|MB|GB|TB)?$', size_str)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2) or 'MB'
    multipliers = {'KB': 0.001, 'MB': 1, 'GB': 1024, 'TB': 1024 * 1024}
    return value * multipliers.get(unit, 1)


def get_resources(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    link_type: str | None = None,
    category_id: int | None = None,
    is_visible: bool | None = None,
    file_size_filter: str | None = None,
) -> dict:
    query = db.query(Resource)

    if keyword:
        query = query.filter(Resource.title.ilike(f"%{keyword}%"))
    if link_type:
        query = query.filter(Resource.link_type == link_type)
    if category_id:
        query = query.filter(Resource.category_id == category_id)
    if is_visible is not None:
        query = query.filter(Resource.is_visible == is_visible)

    if file_size_filter:
        all_resources = query.all()
        filtered_ids = []
        for r in all_resources:
            size_mb = _parse_size_to_mb(r.file_size) if r.file_size else None
            if size_mb is None:
                continue
            if file_size_filter == 'lt100mb' and size_mb < 100:
                filtered_ids.append(r.id)
            elif file_size_filter == '100mb-1gb' and 100 <= size_mb < 1024:
                filtered_ids.append(r.id)
            elif file_size_filter == '1gb-10gb' and 1024 <= size_mb < 10240:
                filtered_ids.append(r.id)
            elif file_size_filter == 'gt10gb' and size_mb >= 10240:
                filtered_ids.append(r.id)
        if filtered_ids:
            query = db.query(Resource).filter(Resource.id.in_(filtered_ids))
        else:
            return {"total": 0, "items": []}

    total = query.count()
    items = (
        query.order_by(desc(Resource.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "link": r.link,
                "link_type": r.link_type,
                "extraction_code": r.extraction_code,
                "category_id": r.category_id,
                "category_name": r.category.name if r.category else None,
                "file_size": r.file_size,
                "created_by": r.created_by,
                "creator_name": r.creator.username if r.creator else None,
                "is_visible": r.is_visible,
                "view_count": r.view_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in items
        ],
    }


def get_resource_by_id(db: Session, resource_id: int) -> Resource | None:
    return db.query(Resource).filter(Resource.id == resource_id).first()


def create_resource(db: Session, data: ResourceCreate, user_id: int) -> dict:
    resource = Resource(**data.model_dump(), created_by=user_id)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return _resource_to_dict(resource)


def update_resource(db: Session, resource_id: int, data: ResourceUpdate) -> dict | None:
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(resource, key, value)
    db.commit()
    db.refresh(resource)
    return _resource_to_dict(resource)


def delete_resource(db: Session, resource_id: int) -> bool:
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        return False
    db.delete(resource)
    db.commit()
    return True


def batch_create_resources(db: Session, data: ResourceBatchCreate, user_id: int) -> dict:
    success_count = 0
    fail_count = 0
    results = []
    for item_data in data.resources:
        try:
            resource = Resource(**item_data.model_dump(), created_by=user_id)
            db.add(resource)
            db.flush()
            success_count += 1
            results.append(_resource_to_dict(resource))
        except Exception as e:
            fail_count += 1
    db.commit()
    return {"success_count": success_count, "fail_count": fail_count, "results": results}


def batch_delete_resources(db: Session, ids: list[int]) -> dict:
    count = db.query(Resource).filter(Resource.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {"deleted_count": count}


def batch_update_visibility(db: Session, ids: list[int], is_visible: bool) -> dict:
    count = db.query(Resource).filter(Resource.id.in_(ids)).update(
        {"is_visible": is_visible}, synchronize_session=False
    )
    db.commit()
    return {"updated_count": count}


def _resource_to_dict(r: Resource) -> dict:
    return {
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "link": r.link,
        "link_type": r.link_type,
        "extraction_code": r.extraction_code,
        "category_id": r.category_id,
        "file_size": r.file_size,
        "created_by": r.created_by,
        "is_visible": r.is_visible,
        "view_count": r.view_count,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }
