import json
import sqlite3
from pathlib import Path


def get_trending(db_path: str | Path, topics: list[str], min_likes: int = 20, limit: int = 10) -> list[dict]:
    """zenn-scout DB からトレンド記事を取得"""
    db = Path(db_path).expanduser()
    if not db.exists():
        return []

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    topic_filters = " OR ".join([f'topics LIKE ?'] * len(topics))
    params = [f'%"{t}"%' for t in topics] + [min_likes, limit]

    rows = conn.execute(
        f"""
        SELECT slug, title, liked_count, bookmarks_count, author_username, topics
        FROM articles
        WHERE ({topic_filters}) AND liked_count >= ?
        ORDER BY liked_count DESC
        LIMIT ?
        """,
        params,
    ).fetchall()
    conn.close()

    return [dict(r) for r in rows]


def get_written_titles(content_repo: str | Path) -> list[str]:
    """zenn-content の既存記事タイトルを取得して重複を避ける"""
    articles_dir = Path(content_repo) / "articles"
    if not articles_dir.exists():
        return []

    titles = []
    for md in articles_dir.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("title:"):
                titles.append(line.replace("title:", "").strip().strip('"').strip("'"))
                break
    return titles
