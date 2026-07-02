import argparse
from pathlib import Path
from .config import load
from .ollama import from_config
from .scout import get_trending, get_written_titles
from .generator import generate_outline, generate_body
from .publisher import write_article, create_pr


def cmd_run(args: argparse.Namespace) -> None:
    cfg = load()
    client = from_config(cfg)

    if not client.is_available():
        print(f"ERROR: Ollama model '{client.model}' not available at {client.base_url}")
        return

    topics = args.topics.split(",") if args.topics else cfg["generation"]["topics"]
    min_likes = cfg["generation"]["min_likes_threshold"]
    db_path = Path(cfg["scout"]["db_path"]).expanduser()
    content_repo = Path(cfg["zenn_content"]["repo_path"]).expanduser()

    written = get_written_titles(content_repo)
    print(f"既存記事: {len(written)} 件")

    for topic in topics:
        print(f"\n[topic] {topic}")
        refs = get_trending(db_path, [topic], min_likes=min_likes)

        if not refs:
            print(f"  scout DB に {topic} の記事がありません。先に zenn-scout fetch を実行してください")
            continue

        outline = generate_outline(client, topic, refs, template=args.template)
        if not outline["title"]:
            print("  outline 生成失敗: タイトルが取得できませんでした")
            continue

        if outline["title"] in written:
            print(f"  スキップ（既存）: {outline['title']}")
            continue

        body = generate_body(client, outline["title"], outline, template=args.template)

        filepath = write_article(
            content_repo,
            outline["title"],
            outline["emoji"],
            body,
            [topic],
        )

        if args.pr:
            pr_url = create_pr(content_repo, filepath, outline["title"])
            print(f"  PR: {pr_url}")
        else:
            print(f"  ドラフト保存済み（--pr で PR 作成）: {filepath}")


def cmd_check(args: argparse.Namespace) -> None:
    cfg = load()
    client = from_config(cfg)
    available = client.is_available()
    print(f"Ollama: {'✅' if available else '❌'} {client.model} @ {client.base_url}")

    db_path = Path(cfg["scout"]["db_path"]).expanduser()
    print(f"Scout DB: {'✅' if db_path.exists() else '❌'} {db_path}")

    content_repo = Path(cfg["zenn_content"]["repo_path"]).expanduser()
    print(f"zenn-content: {'✅' if content_repo.exists() else '❌'} {content_repo}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="zenn-forge")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="記事ドラフトを生成")
    p_run.add_argument("--topics", help="カンマ区切りトピック（省略時は config.yaml）")
    p_run.add_argument("--template", default="tutorial", choices=["tutorial", "roadmap", "resources", "showcase"], help="テンプレート種別")
    p_run.add_argument("--pr", action="store_true", help="zenn-content に PR 作成")

    sub.add_parser("check", help="接続確認")

    args = parser.parse_args()
    {"run": cmd_run, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    main()
