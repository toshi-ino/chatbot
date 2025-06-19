# medii-ai-platform

## 概要
FastAPIを使用したAI APIプラットフォームです。

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
`.env`ファイルを作成し、必要な環境変数を設定してください。

### 3. Docker環境での起動
```bash
# Dockerコンテナをビルドして起動
docker-compose up --build

# コンテナを停止する場合
docker-compose down
```

## 使用方法

### API確認
アプリケーションが起動したら、以下のURLでAPIにアクセスできます：

- API Root: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## テスト

### テストの実行
```bash
# 全テストの実行
pytest

# 詳細な出力でテスト実行
pytest -v
```

## 開発

### コード品質チェック
```bash
# ruffによるリンティング
ruff check .

# ruffによるフォーマット
ruff format .
```

## プロジェクト構成
```
medii-ai-platform/
├── app/                    # アプリケーションコード
│   ├── main.py            # FastAPIメインアプリケーション
│   ├── core/              # 設定とコア機能
│   ├── routers/           # APIルーター
│   ├── services/          # ビジネスロジック
│   └── schemas/           # Pydanticスキーマ
├── tests/                 # テストコード
├── docker-compose.yml     # Docker Compose設定
├── Dockerfile            # Dockerイメージ設定
├── requirements.txt      # 本番依存関係
├── requirements-dev.txt  # 開発依存関係
└── pyproject.toml       # プロジェクト設定
```
