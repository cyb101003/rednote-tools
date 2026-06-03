from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from skill_manifest import SKILL_DEFINITION


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "RealSkill_agent.zip"


SKILL_ENTRY = r'''
from __future__ import annotations

import asyncio
from typing import Any

from core.generator import generate_variants
from core.humanize import humanize_by_llm, rule_based_humanize
from core.judge import detect_ai_score, judge_and_select


def generate(payload: dict[str, Any]) -> dict[str, Any]:
    topic = str(payload.get("topic", "")).strip()
    platform = str(payload.get("platform", "xiaohongshu")).strip()
    style_refs = payload.get("style_refs") or []

    if not topic:
        raise ValueError("topic is required")
    if platform not in {"xiaohongshu", "zhihu", "weibo"}:
        raise ValueError("platform must be one of: xiaohongshu, zhihu, weibo")

    variants = asyncio.run(generate_variants(topic, platform, style_refs))
    verdict = judge_and_select(variants, platform)
    winner_key = verdict.get("winner", "B")
    best_text = variants.get(winner_key) or variants.get("B") or next(iter(variants.values()))
    humanized = humanize_by_llm(best_text)
    final = rule_based_humanize(humanized, platform)
    final_ai_score = detect_ai_score(final)
    risk_label = "low" if final_ai_score > 7 else "medium" if final_ai_score > 4 else "high"

    return {
        "result": final,
        "winner_agent": winner_key,
        "all_variants": variants,
        "scores": verdict.get("scores", {}),
        "ai_detection_risk": risk_label,
        "ai_score": round(final_ai_score, 1),
        "platform": platform,
    }
'''


def copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        package_dir = Path(tmp) / "RealSkill_agent"
        package_dir.mkdir()

        for folder in ["agents", "collectors", "core", "data"]:
            copy_tree(ROOT / folder, package_dir / folder)

        for file_name in ["build_index.py", "requirements_skill.txt"]:
            shutil.copy2(ROOT / file_name, package_dir / file_name)

        (package_dir / "skill_entry.py").write_text(SKILL_ENTRY.strip() + "\n", encoding="utf-8")
        (package_dir / "skill.json").write_text(
            json.dumps(SKILL_DEFINITION, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        if DIST.exists():
            DIST.unlink()
        with zipfile.ZipFile(DIST, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in package_dir.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(package_dir))

    print(f"Built {DIST.name}")


if __name__ == "__main__":
    main()
