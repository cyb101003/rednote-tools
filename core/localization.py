SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "native": "English",
        "directive": (
            "Write the final copy only in natural, conversational English. "
            "Use contractions, concrete details, and a real creator/editor rhythm. "
            "Do not sound like generic marketing AI."
        ),
        "avoid": "Avoid phrases like unlock, elevate, delve, game-changer, seamless, transform, comprehensive guide, and in today's fast-paced world.",
        "samples": """
[Natural English rhythm examples]
Use these as rhythm references only. Do not copy exact sentences.

I thought the hard part was finding better tools.
It wasn't.
The hard part was noticing where my workflow was leaking attention.

Tiny fix that helped this week:
one doc, one messy outline, ten minutes before touching anything else.

Not dramatic. Annoyingly effective.
""",
    },
    "zh": {
        "name": "Simplified Chinese",
        "native": "简体中文",
        "directive": (
            "Write the final copy only in natural Simplified Chinese. "
            "Use a conversational creator voice, like someone actually posting from experience. "
            "Avoid stiff official language, direct English translation, and over-polished sales copy."
        ),
        "avoid": "Avoid AI-ish Chinese openings like 你是否曾经, 在当今时代, 总而言之, 综上所述, 赋能, 打造闭环.",
        "samples": """
[自然中文节奏示例]
只学习节奏，不复制句子。

说实话，这个点我一开始真没当回事。
但试了一次之后发现，它不是那种很夸张的改变，反而是你会默默留下来的小习惯。

尤其是第二步，真的很适合懒人。
不用准备太多，照着做就能明显少走弯路。
""",
    },
    "zhHant": {
        "name": "Traditional Chinese",
        "native": "繁體中文",
        "directive": (
            "Write the final copy only in natural Traditional Chinese. "
            "Use a relaxed local creator tone rather than Mainland-style official wording. "
            "Avoid literal translation from English or Simplified Chinese."
        ),
        "avoid": "Avoid stiff terms like 賦能, 打造閉環, 綜上所述, 在當今時代.",
        "samples": """
[自然繁中節奏示例]
只學節奏，不複製句子。

老實說，這件事我一開始真的沒有太期待。
但用了一陣子才發現，它不是那種很浮誇的改變，而是會慢慢讓你省下很多力氣的小方法。

最有感的是第二點。
不用想太多，先照著做一次就懂。
""",
    },
    "ja": {
        "name": "Japanese",
        "native": "日本語",
        "directive": (
            "Write the final copy only in natural Japanese. "
            "Do not translate from English sentence by sentence. "
            "Use short, lived-in phrasing, soft transitions, and everyday Japanese social media rhythm."
        ),
        "avoid": "Avoid stiff machine-translated Japanese, excessive ですます form, and generic openings like 現代社会において.",
        "samples": """
[自然な日本語のリズム例]
文そのものではなく、間と温度感だけ参考にしてください。

正直、最初はそこまで期待してなかった。
でも一回やってみたら、地味に効くタイプだった。

特にここ。
ちゃんと準備しなくても、先にこれだけ決めておくと迷わない。

派手じゃないけど、続くやつ。
""",
    },
    "ko": {
        "name": "Korean",
        "native": "한국어",
        "directive": (
            "Write the final copy only in natural Korean. "
            "Do not include English except unavoidable product names or platform names. "
            "Make it sound like a real Korean creator or operator, not translated English. "
            "Use casual but readable rhythm, small personal details, and natural sentence endings."
        ),
        "avoid": "Avoid stiff translated Korean, excessive formal endings, and generic AI-style phrases.",
        "samples": """
[자연스러운 한국어 리듬 예시]
문장을 베끼지 말고 말투와 흐름만 참고하세요.

솔직히 처음엔 별 기대 안 했다.
근데 한 번 써보니까, 생각보다 오래 남는 쪽이었다.

특히 이 부분.
거창하게 준비할 필요 없이, 일단 이것만 정해두면 덜 헤맨다.

화려하진 않은데 계속 쓰게 되는 느낌.
""",
    },
    "ms": {
        "name": "Malay",
        "native": "Bahasa Melayu",
        "directive": (
            "Write the final copy only in natural Malay. "
            "Use a conversational Malaysian social media tone. "
            "It can be casual and practical, but avoid awkward direct translation from English."
        ),
        "avoid": "Avoid stiff corporate Malay and literal English structure.",
        "samples": """
[Natural Malay rhythm examples]
Use these as rhythm references only.

Sejujurnya, mula-mula aku tak letak harapan tinggi pun.
Tapi lepas cuba sekali, baru rasa benda ni memang membantu.

Paling terasa dekat bahagian ni.
Tak perlu setup besar-besar, cuma buat langkah kecil dulu.

Simple, tapi senang nak repeat.
""",
    },
    "fr": {
        "name": "French",
        "native": "français",
        "directive": (
            "Write the final copy only in natural French. "
            "Use a conversational, credible French creator voice. "
            "For LinkedIn, keep it professional but human; for casual platforms, keep it lighter and more direct."
        ),
        "avoid": "Avoid literal English translation, excessive corporate buzzwords, and stiff textbook French.",
        "samples": """
[Natural French rhythm examples]
Use these as rhythm references only.

Franchement, je ne pensais pas que ce petit changement ferait une vraie difference.
Et pourtant, c'est souvent ce genre de detail qui reste.

Le plus utile pour moi :
decider du message avant de commencer a produire.

Moins de bruit. Moins d'allers-retours. Beaucoup plus clair.
""",
    },
}


LANGUAGE_ALIASES = {
    "english": "en",
    "simplified chinese": "zh",
    "chinese": "zh",
    "traditional chinese": "zhHant",
    "japanese": "ja",
    "korean": "ko",
    "malay": "ms",
    "french": "fr",
}


def normalize_content_language(value: str | None, fallback: str = "en") -> str:
    raw = (value or fallback or "en").strip()
    if raw == "auto":
        raw = fallback or "en"
    key = LANGUAGE_ALIASES.get(raw.lower(), raw)
    return key if key in SUPPORTED_LANGUAGES else "en"


def language_profile(language: str | None, fallback: str = "en") -> dict:
    key = normalize_content_language(language, fallback)
    return {"key": key, **SUPPORTED_LANGUAGES[key]}


def build_localized_directive(platform: str, content_language: str | None, fallback: str = "en") -> str:
    profile = language_profile(content_language, fallback)
    return (
        f"Output language: {profile['name']} ({profile['native']}).\n"
        f"{profile['directive']}\n"
        f"{profile['avoid']}\n"
        "Hard rule: the publish-ready copy must be written in this output language, not English, unless English itself is selected.\n"
        "Important: The platform controls format and rhythm; the content language controls the actual writing language and local expression.\n"
        "Do not output bilingual copy unless the topic explicitly asks for it.\n"
        "Do not add translation notes, explanations, markdown, headings, bullets, numbered lists, or code fences."
    )
