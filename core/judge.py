import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from agents.prompts import JUDGE_PROMPT

load_dotenv(override=True, encoding="utf-8-sig")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY") or "missing-key",
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def detect_ai_score(text: str) -> float:
    generic_patterns = [
        r"\b(firstly|secondly|finally|in conclusion|comprehensive guide)\b",
        r"\b(unlock|leverage|delve into|it is important to note)\b",
        r"(首先|其次|最后|综上所述|总而言之|毋庸置疑)",
    ]
    score = 10.0
    lower = text.lower()
    for pattern in generic_patterns:
        if re.search(pattern, lower):
            score -= 1.4

    sentences = re.split(r"[。！？.!?\n]+", text)
    longest = max((len(s.strip()) for s in sentences), default=0)
    if longest > 90:
        score -= 1.2
    if text.count("#") > 8:
        score -= 0.8
    return max(1.0, round(score, 1))


def extract_json(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, flags=re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def fallback_scores(variants: dict[str, str], platform: str) -> dict:
    scores = {}
    for key, text in variants.items():
        length = len(text)
        human = detect_ai_score(text)
        platform_fit = 6.0
        spread = 6.0

        if platform == "xiaohongshu":
            if "#" in text:
                platform_fit += 0.7
            if any(word in text for word in ["真的", "就是说", "姐妹", "家人", "宝子", "emmm"]):
                platform_fit += 0.8
            if 160 <= length <= 900:
                spread += 0.8
        elif platform == "zhihu":
            if any(word in text for word in ["原因", "建议", "你会发现", "第一", "第二"]):
                platform_fit += 1.0
            if 260 <= length <= 1200:
                spread += 0.6
        elif platform == "weibo":
            if length <= 360:
                platform_fit += 1.0
            if any(mark in text for mark in ["！", "?", "？"]):
                spread += 0.5

        elif platform in {"x", "twitter"}:
            if length <= 600:
                platform_fit += 0.8
            if "\n" in text or len(text.split()) <= 90:
                spread += 0.6
            if any(word in text.lower() for word in ["thread", "hot take", "here's", "why"]):
                spread += 0.3
        elif platform == "linkedin":
            if 180 <= length <= 1600:
                platform_fit += 0.7
            if any(word in text.lower() for word in ["lesson", "framework", "team", "career", "founder", "leader"]):
                platform_fit += 0.6
            if "\n" in text:
                spread += 0.5
        elif platform in {"instagram", "tiktok"}:
            if length <= 1200:
                platform_fit += 0.6
            if any(word in text.lower() for word in ["save", "watch", "caption", "pov", "hook"]):
                spread += 0.5

        if key == "A":
            spread += 0.5
        elif key == "B":
            human += 0.3
        elif key == "C":
            platform_fit += 0.3

        scores[key] = [
            round(min(human, 10), 1),
            round(min(platform_fit, 10), 1),
            round(min(spread, 10), 1),
        ]
    return scores


def normalize_result(result: dict | None, variants: dict[str, str], platform: str) -> dict:
    scores = result.get("scores") if isinstance(result, dict) else None
    if not isinstance(scores, dict) or not all(k in scores for k in variants):
        scores = fallback_scores(variants, platform)

    clean_scores = {}
    for key in variants:
        raw = scores.get(key, [6, 6, 6])
        if not isinstance(raw, list) or len(raw) < 3:
            raw = [6, 6, 6]
        ai_sc = detect_ai_score(variants[key])
        clean_scores[key] = [
            round((float(raw[0]) + ai_sc) / 2, 1),
            round(float(raw[1]), 1),
            round(float(raw[2]), 1),
        ]

    winner = result.get("winner") if isinstance(result, dict) else None
    if winner not in variants:
        winner = max(clean_scores, key=lambda k: sum(clean_scores[k]))

    strengths = result.get("strengths") if isinstance(result, dict) else {}
    if not isinstance(strengths, dict):
        strengths = {}

    return {
        "winner": winner,
        "reason": result.get("reason", "Fallback scoring selected the strongest balanced draft.") if isinstance(result, dict) else "Fallback scoring selected the strongest balanced draft.",
        "merge_strategy": result.get("merge_strategy", "Use the winning draft as the base and borrow the strongest detail from the other drafts.") if isinstance(result, dict) else "Use the winning draft as the base and borrow the strongest detail from the other drafts.",
        "strengths": {
            "A": strengths.get("A", "Strong hook and opening energy."),
            "B": strengths.get("B", "Natural lived-in voice."),
            "C": strengths.get("C", "Clear structure and save value."),
        },
        "scores": clean_scores,
    }


def judge_and_select(variants: dict, platform: str) -> dict:
    prompt = JUDGE_PROMPT.format(
        platform=platform,
        A=variants["A"],
        B=variants["B"],
        C=variants["C"],
        text_a=variants["A"],
        text_b=variants["B"],
        text_c=variants["C"],
        xhs=platform,
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    raw = resp.choices[0].message.content.strip()
    return normalize_result(extract_json(raw), variants, platform)
