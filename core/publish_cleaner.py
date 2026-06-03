import re


def clean_publish_text(text: str) -> str:
    """Remove Markdown artifacts while keeping readable social-post spacing."""
    if not text:
        return ""

    cleaned = str(text).replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"```[\s\S]*?```", lambda m: m.group(0).strip("`"), cleaned)
    cleaned = re.sub(r"`([^`\n]+)`", r"\1", cleaned)
    cleaned = re.sub(r"(\*\*|__)(.*?)\1", r"\2", cleaned)
    cleaned = re.sub(r"(\*|_)([^*_]+)\1", r"\2", cleaned)
    cleaned = re.sub(r"^\s{0,3}#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s{0,3}>\s?", "", cleaned, flags=re.MULTILINE)

    lines = []
    for raw_line in cleaned.split("\n"):
        line = raw_line.strip()
        line = re.sub(r"^[-*+]\s+", "", line)
        line = re.sub(r"^\d+[\.)]\s+", "", line)
        line = re.sub(r"\s{2,}", " ", line).strip()
        lines.append(line)

    compact_lines = []
    blank_seen = False
    for line in lines:
        if not line:
            if not blank_seen and compact_lines:
                compact_lines.append("")
            blank_seen = True
            continue
        compact_lines.append(line)
        blank_seen = False

    return "\n".join(compact_lines).strip()


def clean_variant_map(variants: dict) -> dict:
    return {key: clean_publish_text(value) for key, value in (variants or {}).items()}
