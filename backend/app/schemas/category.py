from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    sort_order: int
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryWithCount(BaseModel):
    id: int
    name: str
    description: Optional[str]
    resource_count: int = 0

    class Config:
        from_attributes = True
