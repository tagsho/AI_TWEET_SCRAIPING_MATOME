# AI速報まとめ (AI_TWEET_SCRAIPING_MATOME)

AI関連の最新ニュースを最速で集約・要約するためのプロジェクトです。X(旧Twitter)を含む複数ソースからURL単位で情報を収集し、要約とランキングを付与して表示します。

## 構成

- `backend/` – FastAPI + SQLite によるAPIサーバーと収集ロジック
- `frontend/` – シンプルな静的UI (Vanilla JS)
- `config/sources.yaml` – 監視対象ソースの設定

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.init_db
```

### 収集ジョブの実行

`config/sources.yaml`を編集して監視対象を追加できます。以下で1回分の収集を実行します。

```bash
python -m backend.ingest --config config/sources.yaml
```

収集ではURL単位で重複排除し、要約（300字以内・要点3つ・タグ1〜3件）とスコア計算を行います。要約に失敗した場合はレコードのみ登録されます。

### APIサーバーの起動

```bash
uvicorn backend.main:app --reload
```

#### 主なエンドポイント

- `GET /items` – 新着またはバズ順での一覧。`sort`(new|buzz), `tag`, `q`, `source_type`などのフィルタをサポート。
- `GET /items/{id}` – 個別アイテム。
- `POST /mentions` – URLを指定して紹介情報（キュレーター）を追加。X本文などは保存されません。

### フロントエンドの動作確認

`frontend/` ディレクトリを任意の静的ホスティング（`python -m http.server` など）で配信し、バックエンドのAPI (`http://localhost:8000`) を参照するようになっています。

```bash
cd frontend
python -m http.server 3000
```

ブラウザで `http://localhost:3000` を開き、タブ切り替え・キーワード/タグフィルタ・ソース絞り込みが動作することを確認できます。

## 設計メモ

- URL正規化でUTMなどのトラッキングパラメータを除去し、同一URLを1件に統合。
- アイテムとキュレーター紹介（メンション）を分離して保存。
- スコアは「拡散指標 × 鮮度減衰 × ソース重み」を組み合わせ、`/items?sort=buzz`で利用。
- Xの投稿は埋め込みウィジェット表示のみ。本文は保存・再配信していません。

## 今後の拡張アイデア

- Bluesky/Mastodon/Reddit 等の公式クライアント実装
- Web Push通知や影響度分析ダッシュボード
- 誤報フラグなどユーザー参加型の品質管理
