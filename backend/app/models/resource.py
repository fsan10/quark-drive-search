from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    link = Column(String(500), nullable=False)
    link_type = Column(String(20), nullable=False, index=True)
    extraction_code = Column(String(50))
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    file_size = Column(String(50))
    created_by = Column(Integer, ForeignKey("users.id"))
    is_visible = Column(Boolean, default=True, index=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", back_populates="resources")
    category = relationship("Category", back_populates="resources")

    __table_args__ = (
        Index('idx_resources_link_type', 'link_type'),
        Index('idx_resources_category', 'category_id'),
        Index('idx_resources_visible', 'is_visible'),
    )
