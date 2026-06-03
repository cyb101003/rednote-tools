import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from core.xhs_trends import build_xhs_trend_context


_CACHE: dict[str, tuple[float, str]] = {}

PLATFORM_PROFILES = {
    "x": {
        "name": "X / Twitter",
        "env": "X_TREND_FEEDS",
        "query": "site:x.com OR site:twitter.com",
        "rules": [
            "Open with a concise point of view, not a title.",
            "Prefer short lines, one clear tension, and one memorable phrasing.",
            "Avoid threadbait, fake controversy, and generic engagement bait.",
            "Strong posts often combine a sharp observation with a useful takeaway.",
        ],
    },
    "twitter": {
        "name": "X / Twitter",
        "env": "X_TREND_FEEDS",
        "query": "site:x.com OR site:twitter.com",
        "rules": [
            "Open with a concise point of view, not a title.",
            "Prefer short lines, one clear tension, and one memorable phrasing.",
            "Avoid threadbait, fake controversy, and generic engagement bait.",
            "Strong posts often combine a sharp observation with a useful takeaway.",
        ],
    },
    "linkedin": {
        "name": "LinkedIn",
        "env": "LINKEDIN_TREND_FEEDS",
        "query": "site:linkedin.com/posts OR site:linkedin.com/pulse",
        "rules": [
            "Start with a professional but human hook grounded in a real situation.",
            "Use short paragraphs or bullets with a clear lesson, framework, or decision point.",
            "Add credibility through context, not inflated claims.",
            "End with a practical reflection or thoughtful question.",
        ],
    },
    "instagram": {
        "name": "Instagram",
        "env": "INSTAGRAM_TREND_FEEDS",
        "query": "site:instagram.com",
        "rules": [
            "Lead with visual context and a caption that feels personal.",
            "Use a warm, sensory, creator-first rhythm.",
            "Keep the core message easy to skim and save.",
        ],
    },
    "tiktok": {
        "name": "TikTok",
        "env": "TIKTOK_TREND_FEEDS",
        "query": "site:tiktok.com",
        "rules": [
            "Write like a spoken script with a fast first-second hook.",
            "Use scene setup, contrast, and a simple payoff.",
            "Keep each beat easy to perform on camera.",
        ],
    },
}


def _enabled() -> bool:
    return os.getenv("SOCIAL_TREND_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def _timeout_seconds() -> float:
    try:
        return max(2.0, float(os.getenv("SOCIAL_TREND_TIMEOUT", "5")))
    except ValueError:
        return 5.0


def _cache_ttl_seconds() -> int:
    try:
        return max(60, int(os.getenv("SOCIAL_TREND_CACHE_TTL", str(3 * 60 * 60))))
    except ValueError:
        return 3 * 60 * 60


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _feed_urls(topic: str, profile: dict) -> list[str]:
    configured = os.getenv(profile["env"], "").strip()
    if configured:
        return [url.strip() for url in configured.split(";") if url.strip()]

    query = f"{topic} {profile['query']}"
    encoded = urllib.parse.quote(query)
    return [f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"]


def _fetch_feed_titles(url: str, limit: int) -> list[str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "RealSkillTrendFetcher/1.0"},
    )
    with urllib.request.urlopen(req, timeout=_timeout_seconds()) as response:
        payload = response.read(600_000)

    root = ET.fromstring(payload)
    titles: list[str] = []
    for item in root.findall(".//item"):
        title = _clean_text(item.findtext("title", ""))
        if title:
            titles.append(title[:140])
        if len(titles) >= limit:
            break
    return titles


def _public_trend_titles(topic: str, profile: dict, limit: int = 6) -> list[str]:
    titles: list[str] = []
    for url in _feed_urls(topic, profile):
        try:
            titles.extend(_fetch_feed_titles(url, limit - len(titles)))
        except Exception as exc:
            print(f"Public trend feed skipped: {exc}")
        if len(titles) >= limit:
            break
    return list(dict.fromkeys(titles))[:limit]


def _rule_context(platform_key: str, profile: dict) -> str:
    rules = "\n".join(f"- {rule}" for rule in profile["rules"])
    return (
        f"\n\n[{profile['name']} platform writing rules]\n"
        f"{rules}\n"
        "Use these platform-native rules when live trend examples are unavailable."
    )


def _foreign_platform_context(topic: str, platform_key: str, profile: dict) -> str:
    key = f"{platform_key}::{topic.strip().lower()}"
    cached = _CACHE.get(key)
    now = time.time()
    if cached and now - cached[0] < _cache_ttl_seconds():
        return cached[1]

    titles = _public_trend_titles(topic, profile)
    rules = _rule_context(platform_key, profile)
    if titles:
        samples = "\n".join(f"- {title}" for title in titles)
        context = (
            f"\n\n[{profile['name']} public trend signals]\n"
            "These are public trend/search signals, not private scraped data. "
            "Use them to understand recent framing, vocabulary, and audience interest. "
            "Do not copy exact text, accounts, links, or claims.\n"
            f"{samples}"
            f"{rules}"
        )
    else:
        context = rules

    _CACHE[key] = (now, context)
    return context


def build_social_trend_context(topic: str, platform: str, top_n: int = 8) -> str:
    platform_key = (platform or "").strip().lower()
    if platform_key == "xiaohongshu":
        return build_xhs_trend_context(topic, platform, top_n=top_n)
    if not _enabled():
        return ""
    profile = PLATFORM_PROFILES.get(platform_key)
    if not profile:
        return ""
    return _foreign_platform_context(topic, platform_key, profile)
