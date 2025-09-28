from backend.models import Source
from backend.utils.summary import extract_sentences
from backend.utils.url import normalize_url


def test_normalize_url_removes_tracking_params():
    url = "https://example.com/article?utm_source=test&utm_medium=email&id=123"
    normalized = normalize_url(url)
    assert "utm_source" not in normalized
    assert normalized.endswith("id=123")


def test_extract_sentences_handles_japanese_text():
    text = "最新情報をお届けします。次の文も続きます。さらに別の話題です。"
    sentences = extract_sentences(text)
    assert len(sentences) >= 2
    assert sentences[0].endswith("。")


def test_source_display_type_prefers_metadata():
    source = Source(name="tester", type="rss", metadata_json='{"platform": "twitter"}')
    assert source.display_type == "twitter"
