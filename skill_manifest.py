SKILL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "generate_human_like_social_copy",
        "description": "Generate platform-native social media copy through multi-agent competition, creator style references, and trend-aware content memory. Supports Xiaohongshu, X/Twitter, LinkedIn, Instagram, TikTok, Zhihu, and Weibo while reducing generic AI writing patterns.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The writing topic or keyword"
                },
                "platform": {
                    "type": "string",
                    "enum": ["xiaohongshu", "x", "linkedin", "instagram", "tiktok", "zhihu", "weibo"],
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
