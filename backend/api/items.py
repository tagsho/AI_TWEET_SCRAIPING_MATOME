from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models import Item, Mention
from backend.schemas.item import ItemResponse, MentionSummary
from backend.utils.summary import deserialize_list

router = APIRouter(prefix="/items", tags=["items"])


SORT_OPTIONS = {"new": Item.score_new.desc(), "buzz": Item.score_buzz.desc()}


@router.get("/", response_model=list[ItemResponse])
def list_items(
    sort: Literal["new", "buzz"] = Query("new"),
    tag: str | None = Query(None),
    q: str | None = Query(None),
    source_type: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[ItemResponse]:
    order_by = SORT_OPTIONS.get(sort, Item.score_new.desc())
    stmt = (
        select(Item)
        .options(joinedload(Item.mentions).joinedload(Mention.source))
        .order_by(order_by)
        .limit(limit)
        .offset(offset)
    )
    if tag:
        stmt = stmt.where(Item.tags_json.is_not(None)).where(Item.tags_json.contains(f'"{tag}"'))
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                and_(Item.title.is_not(None), Item.title.ilike(like)),
                and_(Item.summary.is_not(None), Item.summary.ilike(like)),
            )
        )
    if source_type:
        stmt = stmt.where(Item.source_type == source_type)
    items = db.scalars(stmt).unique().all()
    return [_item_to_response(item) for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ItemResponse:
    stmt = (
        select(Item)
        .where(Item.id == item_id)
        .options(joinedload(Item.mentions).joinedload(Mention.source))
    )
    item = db.scalars(stmt).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(item)


def _item_to_response(item: Item) -> ItemResponse:
    mentions = []
    for mention in item.mentions:
        source = mention.source
        mentions.append(
            MentionSummary(
                id=mention.id,
                source_name=source.name if source else "",
                source_handle=source.handle if source else None,
                source_type=source.display_type if source else "unknown",
                post_url=mention.post_url,
                embed_html=mention.embed_html,
                like_count=mention.like_count,
                repost_count=mention.repost_count,
                reply_count=mention.reply_count,
            )
        )
    return ItemResponse(
        id=item.id,
        url=item.url,
        normalized_url=item.normalized_url,
        title=item.title,
        summary=item.summary,
        summary_points=deserialize_list(item.summary_points_json),
        tags=deserialize_list(item.tags_json),
        language=item.language,
        score_new=item.score_new,
        score_buzz=item.score_buzz,
        score_raw=item.score_raw,
        published_at=item.published_at,
        last_seen_at=item.last_seen_at,
        source_type=item.source_type,
        mentions=mentions,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
