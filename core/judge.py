import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from agents.prompts import JUDGE_PROMPT

load_dotenv(override=True)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

def detect_ai_score(text: str) -> float:
    AI_PATTERNS = [
        r"(首先|其次|最后|综上所述|总而言之)",
        r"(大概率|一定|绝对|毋庸置疑)",
        r"(第一点|第二点|第三点)",
        r"[A-Za-z]{10,}"
    ]
    score = 10.0
    for pat in AI_PATTERNS:
        if re.search(pat, text):
            score -= 1.5
    sentences = re.split(r"[。！？]", text)
    if len(sentences) > 0 and len(max(sentences, key=len)) > 60:
        score -= 2
    return max(1.0, round(score, 1))

def judge_and_select(variants: dict, platform: str) -> dict:
    platform_map = {
        "xiaohongshu": "小红书",
        "zhihu": "知乎",
        "weibo": "微博"
    }
    cn_plat = platform_map.get(platform, platform)
    # 补齐所有缺失占位：text_a/text_b/text_c/xhs
    prompt = JUDGE_PROMPT.format(
        platform=cn_plat,
        A=variants["A"],
        B=variants["B"],
        C=variants["C"],
        text_a=variants["A"],
        text_b=variants["B"],
        text_c=variants["C"],
        xhs=""
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    raw = resp.choices[0].message.content.strip()
    try:
        result = json.loads(raw)
    except:
        result = {"winner": "B", "reason": "JSON解析失败，默认选B", "scores": {}}
    for k in variants:
        ai_sc = detect_ai_score(variants[k])
        if k in result.get("scores", {}):
            result["scores"][k][0] = round((result["scores"][k][0] + ai_sc) / 2, 1)
    return result
