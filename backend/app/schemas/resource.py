from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResourceCreate(BaseModel):
    title: str
    link: str
    link_type: str
    extraction_code: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    file_size: Optional[str] = None
    is_visible: Optional[bool] = True


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    link: Optional[str] = None
    link_type: Optional[str] = None
    extraction_code: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    file_size: Optional[str] = None
    is_visible: Optional[bool] = None


class ResourceResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    link: str
    link_type: str
    extraction_code: Optional[str]
    category_id: Optional[int]
    file_size: Optional[str]
    created_by: Optional[int]
    is_visible: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ResourceBatchCreate(BaseModel):
    resources: list[ResourceCreate]


class ParsedResource(BaseModel):
    title: str
    link: str
    link_type: str
    extraction_code: Optional[str] = None


class AiParseRequest(BaseModel):
    text: str
    model: str | None = None


class AiParseResponse(BaseModel):
    parsed: list[ParsedResource]


class AiBatchParseResponse(BaseModel):
    success_count: int
    fail_count: int
    results: list[ParsedResource]
