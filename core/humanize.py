import random

from agents.prompts import HUMANIZE_PROMPT
from core.localization import language_profile
from .generator import call_llm_sync

ENGLISH_PLATFORMS = {"x", "twitter", "linkedin", "instagram", "tiktok"}


def humanize_by_llm(text: str, platform: str = "", content_language: str = "en") -> str:
    lang = language_profile(content_language)
    source = f"Target platform: {platform}\nContent language: {lang['name']}\n\n{text}" if platform else text
    prompt = HUMANIZE_PROMPT.format(text=source)
    return call_llm_sync(prompt, temperature=0.9)


def rule_based_humanize(text: str, platform: str, content_language: str = "en") -> str:
    platform = (platform or "").strip().lower()
    language = (content_language or "en").strip()

    if language == "en":
        replacements = {
            "Firstly,": "",
            "In conclusion,": "",
            "It is important to note that": "Worth noting:",
            "In today's fast-paced world,": "",
            "game-changer": "useful shift",
            "Game-changer": "Useful shift",
            "unlock": "make room for",
            "Unlock": "Make room for",
            "elevate": "improve",
            "Elevate": "Improve",
            "delve into": "look at",
            "Delve into": "Look at",
            "seamless": "smooth",
            "transform your": "change your",
            "Transform your": "Change your",
            "comprehensive guide": "practical guide",
            "Comprehensive guide": "Practical guide",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        for cn_filler in ["就是说", "你懂吧", "反正", "宝子", "姐妹", "家人们", "嗯..."]:
            text = text.replace(cn_filler, "")
        return text.strip()

    if language in {"ja", "ko", "ms", "fr", "zhHant"}:
        replacements = {
            "In conclusion,": "",
            "Firstly,": "",
            "game-changer": "useful shift",
            "unlock": "make easier",
            "elevate": "improve",
            "delve into": "look at",
            "comprehensive guide": "practical guide",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.strip()

    fillers = ["就是说", "嗯...", "就那种", "你懂吧", "emmm", "反正"]
    sentences = text.split("。")
    new_sents = []
    for sentence in sentences:
        if sentence and random.random() < 0.3:
            sentence = random.choice(fillers) + "，" + sentence
        new_sents.append(sentence)
    text = "。".join(new_sents)

    if platform == "xiaohongshu":
        replacements = {"的": "滴", "了": "啦", "什么": "啥", "没有": "没有", "非常": "巨"}
        for old, new in replacements.items():
            if random.random() < 0.4:
                text = text.replace(old, new)
        tags = ["#日常", "#分享", "#记录生活", "#吐槽", "#干货"]
        if random.random() < 0.6:
            text += " " + " ".join(random.sample(tags, 2))
    elif platform == "zhihu":
        text = text.replace("一定", "大概率").replace("绝对", "个人觉得")
        text = text.replace("首先", "第一点").replace("其次", "第二点")

    return text.strip()
