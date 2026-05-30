SKILL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "generate_human_like_social_copy",
        "description": "Generate highly human-like, AI-detection-resistant social media copy through multi-agent competition and real viral content reference. Supports Xiaohongshu, Zhihu, and Weibo styles. Effectively avoids platform shadowbans.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The writing topic or keyword"
                },
                "platform": {
                    "type": "string",
                    "enum": ["xiaohongshu", "zhihu", "weibo"],
                    "description": "Target social media platform"
                },
                "style_refs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional reference viral posts for style imitation"
                }
            },
            "required": ["topic", "platform"]
        }
    }
}
