from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

import httpx
from bs4 import BeautifulSoup
from readability import Document
from slugify import slugify

STOPWORDS = {
    "the",
    "and",
    "for",
    "that",
    "with",
    "have",
    "this",
    "from",
    "your",
    "about",
    "https",
    "http",
    "www",
    "com",
}


@dataclass
class Summary:
    text: str
    bullet_points: list[str]
    tags: list[str]
    language: str


class SummaryError(Exception):
    pass


def fetch_article_text(url: str) -> str:
    headers = {"User-Agent": "AI-MatomeBot/0.1"}
    with httpx.Client(timeout=10) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
    document = Document(html)
    summary_html = document.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, "html.parser")
    text = " ".join(p.get_text(separator=" ", strip=True) for p in soup.find_all("p"))
    if not text:
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
    return text


def truncate_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    truncated = text[: limit - 1]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated + "…"


SENTENCE_SPLIT = re.compile(r"(?<=[。．.!?？])")


def extract_sentences(text: str, max_sentences: int = 5) -> list[str]:
    candidates = re.split(SENTENCE_SPLIT, text)
    filtered = [c.strip() for c in candidates if c.strip()]
    return filtered[:max_sentences]


TAG_SPLIT = re.compile(r"[^A-Za-z0-9ぁ-んァ-ヴ一-龠+#-]+")


def extract_tags(text: str, max_tags: int = 3) -> list[str]:
    tokens = [token.lower() for token in TAG_SPLIT.split(text) if token]
    tokens = [token for token in tokens if token not in STOPWORDS and len(token) > 2]
    scores = Counter(tokens)
    top_tokens = [slugify(word, separator="-") for word, _ in scores.most_common(max_tags * 2)]
    unique: list[str] = []
    for token in top_tokens:
        if token not in unique:
            unique.append(token)
        if len(unique) >= max_tags:
            break
    return unique[:max_tags]


LANGUAGE_HINTS = {
    "の": "ja",
    "する": "ja",
    "the": "en",
    "with": "en",
}


def detect_language(text: str) -> str:
    for hint, lang in LANGUAGE_HINTS.items():
        if hint in text.lower():
            return lang
    return "ja"


def summarize_url(url: str) -> Summary:
    text = fetch_article_text(url)
    sentences = extract_sentences(text)
    if not sentences:
        raise SummaryError("No sentences extracted")
    summary_text = truncate_text(" ".join(sentences), 300)
    bullet_points = [truncate_text(sentence, 120) for sentence in sentences[:3]]
    tags = extract_tags(text)
    language = detect_language(text)
    return Summary(text=summary_text, bullet_points=bullet_points, tags=tags, language=language)


def serialize_points(points: Iterable[str]) -> str:
    return json.dumps(list(points), ensure_ascii=False)


def serialize_tags(tags: Iterable[str]) -> str:
    return json.dumps(list(tags), ensure_ascii=False)


def deserialize_list(data: str | None) -> list[str]:
    if not data:
        return []
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return []
