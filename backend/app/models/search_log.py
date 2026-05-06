from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime
from app.database import Base


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), nullable=False, index=True)
    result_count = Column(Integer, default=0)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_search_logs_keyword', 'keyword'),
        Index('idx_search_logs_created', 'created_at'),
    )
