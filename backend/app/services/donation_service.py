from sqlalchemy.orm import Session
from app.models.donation_config import DonationConfig


def get_donation_config(db: Session) -> dict:
    config = db.query(DonationConfig).first()
    if not config:
        config = DonationConfig(content="暂无打赏信息")
        db.add(config)
        db.commit()
        db.refresh(config)
    return {
        "id": config.id,
        "content": config.content,
        "updated_at": config.updated_at.isoformat() if config.updated_at else None,
    }


def update_donation_config(db: Session, content: str, user_id: int) -> dict:
    config = db.query(DonationConfig).first()
    if not config:
        config = DonationConfig(content=content, updated_by=user_id)
        db.add(config)
    else:
        config.content = content
        config.updated_by = user_id
    db.commit()
    db.refresh(config)
    return {
        "id": config.id,
        "content": config.content,
        "updated_at": config.updated_at.isoformat() if config.updated_at else None,
    }
