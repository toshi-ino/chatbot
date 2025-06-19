# Main Application (main.py)

## 概要
MEDII AI Platformのメインアプリケーションファイルです。FastAPIアプリケーションのエントリーポイントとして機能し、CORS設定やルーティングの設定を行います。

## 主要な機能

### FastAPIアプリケーションの初期化
- アプリケーション名: `MEDII AI PLATFORM`
- デバッグモードの設定
- 設定値は `app.core.config` から取得

### CORS設定
全オリジンからのアクセスを許可する設定で、以下を許可しています：
- すべてのオリジン (`*`)  
- 認証情報の送信
- すべてのHTTPメソッド
- すべてのHTTPヘッダー

### ルーター設定
- **medii_q ルーター**: `/api` プレフィックスで登録
- タグ: `medii_q`

### エンドポイント

#### `GET /`
- **目的**: 疎通確認用のエンドポイント
- **レスポンス**: `{"message": "AI API is running"}`

## 依存関係
- `fastapi`: Webフレームワーク
- `fastapi.middleware.cors`: CORS対応
- `dotenv`: 環境変数の読み込み
- `app.core.config`: アプリケーション設定
- `app.routers.medii_q`: APIルーター

## 設定ファイル
ルートディレクトリの `.env` ファイルから環境変数を読み込みます。
