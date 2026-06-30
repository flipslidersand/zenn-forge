# zenn-forge

Zenn 記事の自動生成パイプライン。zenn-scout のトレンドデータを元に Ollama (qwen2.5:7b) でチュートリアル記事ドラフトを生成し、zenn-content に PR を作成する。

## セットアップ

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

## 事前準備

```bash
# 1. zenn-scout でデータ収集
cd ../zenn-scout && zenn-scout fetch --topics rust,go,python --pages 3

# 2. 接続確認
zenn-forge check
```

## 使い方

```bash
# ドラフト生成（ファイル保存のみ）
zenn-forge run --topics rust

# ドラフト生成 + zenn-content に draft PR 作成
zenn-forge run --topics rust,go --pr

# config.yaml のトピックを全処理
zenn-forge run --pr
```

## 設定

`config.yaml` で以下を変更可能：

| キー                             | 説明                                 |
| -------------------------------- | ------------------------------------ |
| `ollama.model`                   | 使用モデル（デフォルト: qwen2.5:7b） |
| `generation.topics`              | 対象トピック                         |
| `generation.min_likes_threshold` | 参考にする記事のいいね数下限         |
| `scout.db_path`                  | zenn-scout の SQLite パス            |
| `zenn_content.repo_path`         | zenn-content のローカルパス          |
