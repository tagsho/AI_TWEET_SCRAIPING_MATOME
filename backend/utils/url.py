from __future__ import annotations

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ref", "fbclid", "gclid"}


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    query_params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k not in TRACKING_PARAMS]
    normalized_query = urlencode(query_params, doseq=True)
    normalized = parsed._replace(query=normalized_query, fragment="")
    if normalized.scheme == "":
        normalized = normalized._replace(scheme="https")
    return urlunparse(normalized)
