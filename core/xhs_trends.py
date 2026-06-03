import os
import re
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_FETCHER = (
    Path.home()
    / ".codex"
    / "skills"
    / "xhs-weekly-ranking-1.0.3"
    / "scripts"
    / "xhs_weekly_fetcher.py"
)

_CACHE: dict[str, tuple[float, str]] = {}


def _enabled() -> bool:
    return os.getenv("XHS_TREND_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def _timeout_seconds() -> float:
    try:
        return max(2.0, float(os.getenv("XHS_TREND_TIMEOUT", "7")))
    except ValueError:
        return 7.0


def _cache_ttl_seconds() -> int:
    try:
        return max(60, int(os.getenv("XHS_TREND_CACHE_TTL", str(6 * 60 * 60))))
    except ValueError:
        return 6 * 60 * 60


def _fetcher_path() -> Path:
    return Path(os.getenv("XHS_WEEKLY_FETCHER_PATH", str(DEFAULT_FETCHER)))


def _clean_cell(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " | ", text, flags=re.I)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" |")


def _extract_table_rows(stdout: str, limit: int = 8) -> list[str]:
    rows: list[str] = []
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line.startswith("|") or "---" in line or "排名" in line:
            continue
        cells = [_clean_cell(cell) for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        rank, note, interaction = cells[0], cells[1], cells[2]
        title = note.split(" | ", 1)[0].strip()
        if not title or title == "笔记信息":
            continue
        rows.append(f"{rank}. {title[:90]} | interaction: {interaction[:28]}")
        if len(rows) >= limit:
            break
    return rows


def _run_fetcher(topic: str, top_n: int = 8) -> str:
    fetcher = _fetcher_path()
    if not fetcher.exists():
        return ""

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [
            sys.executable,
            str(fetcher),
            "--keyword",
            topic,
            "--top_n",
            str(top_n),
        ],
        cwd=str(fetcher.parent),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=_timeout_seconds(),
    )
    if proc.returncode != 0:
        return ""
    rows = _extract_table_rows(proc.stdout, top_n)
    if not rows:
        return ""
    return "\n".join(rows)


def build_xhs_trend_context(topic: str, platform: str, top_n: int = 8) -> str:
    if not _enabled() or platform != "xiaohongshu":
        return ""

    key = f"{topic.strip().lower()}::{top_n}"
    cached = _CACHE.get(key)
    now = time.time()
    if cached and now - cached[0] < _cache_ttl_seconds():
        return cached[1]

    try:
        ranking = _run_fetcher(topic, top_n=top_n)
    except Exception as exc:
        print(f"XHS trend fetch skipped: {exc}")
        return ""

    if not ranking:
        return ""

    context = (
        "\n\n[Xiaohongshu 7-day ranking trend signals]\n"
        "These are live ranking signals from the xhs-weekly-ranking skill. "
        "Use them to understand current hooks, topic framing, and interaction patterns. "
        "Do not copy exact titles, links, creator names, or private facts.\n"
        f"{ranking}\n"
        "Generation guidance: borrow the winning rhythm and user-value angle, "
        "but write an original post for the user's topic."
    )
    _CACHE[key] = (now, context)
    return context
