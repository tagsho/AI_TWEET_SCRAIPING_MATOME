from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SourceCreate(BaseModel):
    name: str
    type: str
    handle: Optional[str] = None
    url: Optional[HttpUrl] = None
    weight: Optional[float] = Field(default=1.0, ge=0)
    metadata_json: Optional[str] = None


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    handle: Optional[str]
    url: Optional[HttpUrl]
    weight: float
    metadata_json: Optional[str]
    created_at: datetime
    updated_at: datetime
