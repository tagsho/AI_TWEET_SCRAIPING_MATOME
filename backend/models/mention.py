from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Mention(Base, TimestampMixin):
    __tablename__ = "mentions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    external_id: Mapped[str | None] = mapped_column(String(255), index=True)
    post_url: Mapped[str | None] = mapped_column(String(500))
    embed_html: Mapped[str | None] = mapped_column(String)
    note: Mapped[str | None] = mapped_column(String)
    like_count: Mapped[int | None] = mapped_column(Integer)
    repost_count: Mapped[int | None] = mapped_column(Integer)
    reply_count: Mapped[int | None] = mapped_column(Integer)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    item: Mapped["Item"] = relationship(back_populates="mentions")
    source: Mapped["Source"] = relationship(back_populates="mentions")
