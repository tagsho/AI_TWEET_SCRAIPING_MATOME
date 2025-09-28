from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select

from backend.database import session_scope
from backend.models import Item, Mention, Source
from backend.services.scoring import compute_item_scores
from backend.utils import summary as summary_utils
from backend.utils.url import normalize_url

from .rss import RSSFetcher


def _resolve_source_type(config: dict[str, Any]) -> str:
    metadata = config.get("metadata") or {}
    return (
        config.get("source_type")
        or metadata.get("platform")
        or metadata.get("source_type")
        or config.get("type")
        or "unknown"
    )


class IngestManager:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        with self.config_path.open("r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def run_once(self) -> None:
        sources = self.config.get("sources", [])
        for source_config in sources:
            ingest_type = source_config["type"]
            if ingest_type == "rss":
                self._ingest_rss(source_config)
            else:
                # Placeholder for other source types
                continue

    def _get_or_create_source(self, config: dict[str, Any]) -> Source:
        name = config["name"]
        handle = config.get("handle")
        with session_scope() as session:
            stmt = select(Source).where(Source.name == name)
            source = session.scalars(stmt).first()
            display_type = _resolve_source_type(config)
            metadata = config.get("metadata", {})
            if source:
                source.type = display_type
                source.handle = handle
                source.url = config.get("url")
                source.weight = config.get("weight", 1.0)
                source.metadata_json = json.dumps(metadata, ensure_ascii=False)
                session.add(source)
                session.flush()
                return source
            source = Source(
                name=name,
                handle=handle,
                type=display_type,
                url=config.get("url"),
                weight=config.get("weight", 1.0),
                metadata_json=json.dumps(metadata, ensure_ascii=False),
            )
            session.add(source)
            session.flush()
            return source

    def _ingest_rss(self, config: dict[str, Any]) -> None:
        fetcher = RSSFetcher(config["feed_url"])
        source = self._get_or_create_source(config)
        for entry in fetcher.fetch():
            self._upsert_item(entry.url, source, title=entry.title, published_at=entry.published_at)

    def _upsert_item(self, url: str, source: Source, title: str | None = None, published_at: datetime | None = None) -> None:
        normalized = normalize_url(url)
        with session_scope() as session:
            stmt = select(Item).where(Item.normalized_url == normalized)
            item = session.scalars(stmt).first()
            if item is None:
                item = Item(
                    url=url,
                    normalized_url=normalized,
                    title=title,
                    published_at=published_at,
                    last_seen_at=datetime.now(UTC),
                    source_type=source.type,
                )
                session.add(item)
                session.flush()

                try:
                    summary = summary_utils.summarize_url(url)
                    item.summary = summary.text
                    item.summary_points_json = summary_utils.serialize_points(summary.bullet_points)
                    item.tags_json = summary_utils.serialize_tags(summary.tags)
                    item.language = summary.language
                except Exception:
                    # Summary failures shouldn't stop ingestion
                    pass
            else:
                item.last_seen_at = datetime.now(UTC)
                if published_at and (item.published_at is None or item.published_at < published_at):
                    item.published_at = published_at
                if title and not item.title:
                    item.title = title
                if not item.source_type:
                    item.source_type = source.type
            mention_stmt = select(Mention).where(Mention.item_id == item.id, Mention.source_id == source.id)
            mention = session.scalars(mention_stmt).first()
            if mention is None:
                mention = Mention(item_id=item.id, source_id=source.id, source=source)
                session.add(mention)
                item.mentions.append(mention)
            mention.fetched_at = datetime.now(UTC)
            compute_item_scores(item)
            session.add(item)
