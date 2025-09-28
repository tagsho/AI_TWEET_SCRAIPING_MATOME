from datetime import UTC, datetime, timedelta

from backend.models import Item, Mention, Source
from backend.services.scoring import compute_item_scores


def make_item_with_mention(like_count=1, repost_count=0, reply_count=0, minutes_ago=10, weight=1.0):
    source = Source(name="tester", type="rss", weight=weight)
    item = Item(
        url="https://example.com",
        normalized_url="https://example.com",
        last_seen_at=datetime.now(UTC) - timedelta(minutes=minutes_ago),
    )
    mention = Mention(source=source, like_count=like_count, repost_count=repost_count, reply_count=reply_count)
    item.mentions.append(mention)
    return item


def test_score_increases_with_engagement():
    item_low = make_item_with_mention(like_count=1)
    item_high = make_item_with_mention(like_count=100)
    compute_item_scores(item_low)
    compute_item_scores(item_high)
    assert item_high.score_raw > item_low.score_raw


def test_score_decay_over_time():
    item_fresh = make_item_with_mention(minutes_ago=1)
    item_old = make_item_with_mention(minutes_ago=500)
    compute_item_scores(item_fresh)
    compute_item_scores(item_old)
    assert item_fresh.score_buzz > item_old.score_buzz
