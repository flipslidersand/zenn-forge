import os
from pathlib import Path
import yaml

_DEFAULT = Path(__file__).parent.parent.parent / "config.yaml"


def load(path: Path = _DEFAULT) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)

    # 環境変数でパスを上書き可能（GitHub Actions self-hosted runner 用）
    if db := os.environ.get("ZENN_SCOUT_DB"):
        cfg["scout"]["db_path"] = db
    if content := os.environ.get("ZENN_CONTENT_REPO"):
        cfg["zenn_content"]["repo_path"] = content

    return cfg
