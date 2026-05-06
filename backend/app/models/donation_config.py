from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class DonationConfig(Base):
    __tablename__ = "donation_configs"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    updated_by = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
