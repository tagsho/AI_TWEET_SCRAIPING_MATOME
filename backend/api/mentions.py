from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Item, Mention, Source
from backend.schemas.mention import MentionCreate, MentionResponse
from backend.services.scoring import compute_item_scores
from backend.utils.url import normalize_url

router = APIRouter(prefix="/mentions", tags=["mentions"])


@router.post("/", response_model=MentionResponse)
def create_mention(payload: MentionCreate, db: Session = Depends(get_db)) -> MentionResponse:
    normalized = normalize_url(str(payload.item_url))
    stmt = select(Item).where(Item.normalized_url == normalized)
    item = db.scalars(stmt).first()
    if item is None:
        item = Item(
            url=str(payload.item_url),
            normalized_url=normalized,
            title=None,
            last_seen_at=datetime.now(UTC),
            source_type=payload.source_type,
        )
        db.add(item)
        db.flush()

    source_stmt = select(Source).where(Source.name == payload.source_name)
    source = db.scalars(source_stmt).first()
    if source is None:
        source = Source(
            name=payload.source_name,
            handle=payload.source_handle,
            type=payload.source_type,
            url=str(payload.source_url) if payload.source_url else None,
        )
        db.add(source)
        db.flush()
    else:
        if payload.source_handle and source.handle != payload.source_handle:
            source.handle = payload.source_handle
        if payload.source_url and source.url != str(payload.source_url):
            source.url = str(payload.source_url)
        if payload.source_type and source.type != payload.source_type:
            source.type = payload.source_type
        db.add(source)

    lookup_conditions = [Mention.item_id == item.id, Mention.source_id == source.id]
    if payload.external_id:
        lookup_conditions.append(Mention.external_id == payload.external_id)
    elif payload.post_url:
        lookup_conditions.append(Mention.post_url == str(payload.post_url))
    mention_stmt = select(Mention).where(and_(*lookup_conditions))
    mention = db.scalars(mention_stmt).first()

    if mention is None:
        mention = Mention(
            item=item,
            source=source,
            post_url=str(payload.post_url) if payload.post_url else None,
            external_id=payload.external_id,
            embed_html=payload.embed_html,
            like_count=payload.like_count,
            repost_count=payload.repost_count,
            reply_count=payload.reply_count,
            note=payload.note,
            fetched_at=datetime.now(UTC),
        )
        db.add(mention)
    else:
        if payload.post_url:
            mention.post_url = str(payload.post_url)
        if payload.embed_html is not None:
            mention.embed_html = payload.embed_html
        if payload.external_id:
            mention.external_id = payload.external_id
        if payload.note is not None:
            mention.note = payload.note
        if payload.like_count is not None:
            mention.like_count = payload.like_count
        if payload.repost_count is not None:
            mention.repost_count = payload.repost_count
        if payload.reply_count is not None:
            mention.reply_count = payload.reply_count
        mention.fetched_at = datetime.now(UTC)

    item.last_seen_at = datetime.now(UTC)
    if payload.published_at and (item.published_at is None or item.published_at < payload.published_at):
        item.published_at = payload.published_at
    if payload.source_type and (not item.source_type or item.source_type == "unknown"):
        item.source_type = payload.source_type
    compute_item_scores(item)
    db.add(item)
    db.commit()
    db.refresh(mention)
    return MentionResponse.model_validate(mention)
