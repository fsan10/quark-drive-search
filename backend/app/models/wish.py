from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Wish(Base):
    __tablename__ = "wishes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    is_resolved = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    replies = relationship("WishReply", back_populates="wish", cascade="all, delete-orphan")


class WishReply(Base):
    __tablename__ = "wish_replies"

    id = Column(Integer, primary_key=True, index=True)
    wish_id = Column(Integer, ForeignKey("wishes.id"), index=True)
    content = Column(Text, nullable=False)
    resource_link = Column(String(500))
    resource_link_type = Column(String(20))
    resource_extraction_code = Column(String(50))
    resource_title = Column(String(200))
    replied_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    wish = relationship("Wish", back_populates="replies")
    admin = relationship("User", foreign_keys=[replied_by])
