from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class MentionCreate(BaseModel):
    item_url: HttpUrl
    source_name: str
    source_type: str
    source_handle: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    post_url: Optional[HttpUrl] = None
    external_id: Optional[str] = None
    embed_html: Optional[str] = None
    like_count: Optional[int] = Field(default=None, ge=0)
    repost_count: Optional[int] = Field(default=None, ge=0)
    reply_count: Optional[int] = Field(default=None, ge=0)
    note: Optional[str] = None
    published_at: Optional[datetime] = None


class MentionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    source_id: int
    post_url: Optional[HttpUrl]
    external_id: Optional[str]
    embed_html: Optional[str]
    like_count: Optional[int]
    repost_count: Optional[int]
    reply_count: Optional[int]
    created_at: datetime
    updated_at: datetime
