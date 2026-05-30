SKILL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "generate_human_like_social_copy",
        "description": "通过多智能体博弈和真实爆款参考，生成高度拟人化、去AI检测的社交媒体文案，支持小红书/知乎/微博风格，有效规避平台限流。",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "写作主题或关键词"
                },
                "platform": {
                    "type": "string",
                    "enum": ["xiaohongshu", "zhihu", "weibo"],
                    "description": "目标平台"
                },
                "style_refs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "可选参考的爆款文案片段（用于风格模仿）"
                }
            },
            "required": ["topic", "platform"]
        }
    }
}
