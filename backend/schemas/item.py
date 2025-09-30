from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class MentionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    source_handle: Optional[str]
    source_type: str
    post_url: Optional[HttpUrl]
    embed_html: Optional[str]
    like_count: Optional[int]
    repost_count: Optional[int]
    reply_count: Optional[int]


class ItemBase(BaseModel):
    url: HttpUrl
    normalized_url: HttpUrl
    title: Optional[str] = None
    summary: Optional[str] = None
    summary_points: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    score_new: float
    score_buzz: float
    score_raw: float
    published_at: Optional[datetime]
    last_seen_at: Optional[datetime]
    source_type: Optional[str] = None


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mentions: List[MentionSummary]
    created_at: datetime
    updated_at: datetime
