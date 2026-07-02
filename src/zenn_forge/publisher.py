import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    s = re.sub(r"[\s_]+", "-", s)
    return s[:40].strip("-") or "article"


def build_frontmatter(title: str, emoji: str, topics: list[str]) -> str:
    safe_topics = json.dumps(topics[:5], ensure_ascii=False)
    return f"""---
title: "{title}"
emoji: "{emoji}"
type: "tech"
topics: {safe_topics}
published: false
---

"""


def write_article(content_repo: str | Path, title: str, emoji: str, body: str, topics: list[str]) -> Path:
    articles_dir = Path(content_repo) / "articles"
    articles_dir.mkdir(exist_ok=True)

    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    slug = f"{date_str}-{_slug(title)}"
    filepath = articles_dir / f"{slug}.md"

    content = build_frontmatter(title, emoji, topics) + body
    filepath.write_text(content, encoding="utf-8")
    print(f"  [write] {filepath}")
    return filepath


def create_pr(content_repo: str | Path, filepath: Path, title: str) -> str:
    repo = Path(content_repo).resolve()
    branch = f"draft/{filepath.stem}"
    # git add にはリポジトリ内の相対パスを渡す
    rel_path = str(filepath.resolve().relative_to(repo))

    subprocess.run(["git", "-C", str(repo), "checkout", "-b", branch], check=True)
    subprocess.run(["git", "-C", str(repo), "add", rel_path], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", f"draft: {title}"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "push", "-u", "origin", branch], check=True)

    result = subprocess.run(
        [
            "gh", "pr", "create",
            "--repo", "flipslidersand/zenn-content",
            "--title", f"[draft] {title}",
            "--body", f"自動生成ドラフト\n\n- [ ] 内容確認\n- [ ] published: true に変更",
            "--draft",
            "--base", "main",
        ],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "-C", str(repo), "checkout", "main"], check=True)
    return result.stdout.strip()
