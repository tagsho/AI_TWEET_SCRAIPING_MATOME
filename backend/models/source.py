from __future__ import annotations

import json
from typing import Any

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    handle: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(50))
    url: Mapped[str | None] = mapped_column(String(500))
    weight: Mapped[float] = mapped_column(default=1.0)
    metadata_json: Mapped[str | None] = mapped_column(String)

    mentions: Mapped[list["Mention"]] = relationship(back_populates="source")

    @property
    def metadata_dict(self) -> dict[str, Any]:
        if not self.metadata_json:
            return {}
        try:
            return json.loads(self.metadata_json)
        except json.JSONDecodeError:
            return {}

    @property
    def display_type(self) -> str:
        metadata = self.metadata_dict
        return metadata.get("platform") or metadata.get("source_type") or self.type
