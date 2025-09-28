from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Item(Base, TimestampMixin):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    normalized_url: Mapped[str] = mapped_column(String(500), index=True)
    title: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)
    summary_points_json: Mapped[str | None] = mapped_column(Text)
    tags_json: Mapped[str | None] = mapped_column(String)
    language: Mapped[str | None] = mapped_column(String(20))
    source_type: Mapped[str | None] = mapped_column(String(50))
    score_raw: Mapped[float] = mapped_column(Float, default=0.0)
    score_buzz: Mapped[float] = mapped_column(Float, default=0.0)
    score_new: Mapped[float] = mapped_column(Float, default=0.0)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    mentions: Mapped[list["Mention"]] = relationship(back_populates="item", cascade="all, delete-orphan")
