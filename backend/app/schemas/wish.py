from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WishCreate(BaseModel):
    content: str


class WishReplyCreate(BaseModel):
    content: str
    resource_link: Optional[str] = None
    resource_link_type: Optional[str] = None
    resource_extraction_code: Optional[str] = None
    resource_title: Optional[str] = None


class DonationConfigUpdate(BaseModel):
    content: str
