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
- **v1 APIルーター**: `/api/v1` プレフィックスで登録
- ルーター統合: `app.routers.v1.v1_router` を使用
- バージョン管理: 将来的なv2, v3追加に対応

### エンドポイント

#### `GET /`
- **目的**: 疎通確認用のエンドポイント
- **レスポンス**: `{"message": "AI API is running"}`

## バージョン管理

### v1 API構造
- **ベースURL**: `/api/v1`
- **統合ルーター**: `v1_router` により各機能別ルーターを統合
- **機能別分類**: Swagger UIでは `medii_q` タグで分類表示

### 将来の拡張
- 新バージョン（v2, v3等）の追加が容易
- 既存バージョンとの並行運用が可能
- 段階的な移行とレガシーサポートに対応

## 依存関係
- `fastapi`: Webフレームワーク
- `fastapi.middleware.cors`: CORS対応
- `dotenv`: 環境変数の読み込み
- `app.core.config`: アプリケーション設定
- `app.routers.v1`: v1 APIルーター

## 設定ファイル
ルートディレクトリの `.env` ファイルから環境変数を読み込みます。
