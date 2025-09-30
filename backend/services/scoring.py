from __future__ import annotations

from datetime import UTC, datetime

from backend.models import Item, Mention, Source

FRESHNESS_HALF_LIFE_MINUTES = 120


def freshness_decay(last_seen_at: datetime | None) -> float:
    if last_seen_at is None:
        return 1.0
    now = datetime.now(UTC)
    age_minutes = (now - last_seen_at).total_seconds() / 60
    if age_minutes <= 0:
        return 1.0
    half_life = FRESHNESS_HALF_LIFE_MINUTES
    decay = 0.5 ** (age_minutes / half_life)
    return max(decay, 0.05)


def compute_mention_score(mention: Mention, source: Source) -> float:
    engagement = (mention.like_count or 0) + 2 * (mention.repost_count or 0) + 0.5 * (mention.reply_count or 0)
    return max(1.0, engagement) * source.weight


def compute_item_scores(item: Item) -> None:
    total_raw = 0.0
    for mention in item.mentions:
        if mention.source is None:
            continue
        total_raw += compute_mention_score(mention, mention.source)
    freshness = freshness_decay(item.last_seen_at)
    item.score_raw = total_raw
    item.score_new = total_raw + freshness
    item.score_buzz = total_raw * freshness
