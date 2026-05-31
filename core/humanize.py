import random
from .generator import call_llm_sync
from agents.prompts import HUMANIZE_PROMPT

def humanize_by_llm(text: str) -> str:
    prompt = HUMANIZE_PROMPT.format(text=text)
    return call_llm_sync(prompt, temperature=0.9)

def rule_based_humanize(text: str, platform: str) -> str:
    fillers = ["就是说", "嗯…", "就那种", "你懂吧", "emmm", "反正"]
    sentences = text.split("。")
    new_sents = []
    for s in sentences:
        if s and random.random() < 0.3:
            s = random.choice(fillers) + "，" + s
        new_sents.append(s)
    text = "。".join(new_sents)

    if platform == "xiaohongshu":
        rep = {"的": "滴", "了": "啦", "什么": "啥", "没有": "🈚️", "非常": "巨"}
        for k, v in rep.items():
            if random.random() < 0.4:
                text = text.replace(k, v)
        tags = ["#日常", "#分享", "#记录生活", "#吐槽", "#干货"]
        if random.random() < 0.6:
            text += " " + " ".join(random.sample(tags, 2))
    elif platform == "zhihu":
        text = text.replace("一定", "大概率").replace("绝对", "个人觉得")
        text = text.replace("首先", "第一点").replace("其次", "第二点")
    return text
