# v1 Router Integration (routers/v1/__init__.py)

## 概要
v1 APIバージョンの統合ルーターを管理するモジュールです。各機能別ルーターを統合し、統一されたv1 APIインターフェースを提供します。

## 主要機能

### v1ルーターの統合
- **統合ルーター**: `v1_router = APIRouter()`
- **機能別ルーター**: 各機能モジュールのルーターを統合
- **タグ管理**: Swagger UIでの分類表示を制御

### 機能別ルーターの登録

#### MediiQ ルーター
```python
v1_router.include_router(medii_q_router, tags=["medii_q"])
```

- **ソースモジュール**: `app.routers.v1.medii_q`
- **エイリアス**: `medii_q_router`
- **Swaggerタグ**: `medii_q`

## 設計思想

### 統合管理
- **一元化**: 全てのv1 APIエンドポイントを一箇所で管理
- **拡張性**: 新しい機能モジュールの追加が容易
- **保守性**: バージョン固有の設定や変更の管理

### バージョン分離
- **独立性**: 他のバージョンから完全に分離
- **並行運用**: v2, v3等との同時提供が可能
- **段階的移行**: 新バージョンへのスムーズな移行をサポート

## アーキテクチャ

### ディレクトリ構造
```
app/routers/v1/
├── __init__.py      # 統合ルーター（このファイル）
└── medii_q.py       # MediiQ関連エンドポイント
```

### データフロー
1. **main.py** が `v1_router` をインポート
2. **v1_router** が各機能別ルーターを統合
3. **機能別ルーター** が実際のエンドポイント処理を実行

### 依存関係
```
main.py
    ↓ import v1_router
routers/v1/__init__.py
    ↓ import medii_q_router
routers/v1/medii_q.py
    ↓ import services
services/
```

## 将来の拡張

### 新機能の追加
新しい機能（例：`document_search`）を追加する場合：

1. **新ファイル作成**: `app/routers/v1/document_search.py`
2. **ルーター定義**: `router = APIRouter()`
3. **統合追加**: `__init__.py` でルーターを追加

```python
from .document_search import router as document_search_router
v1_router.include_router(document_search_router, tags=["document-search"])
```

### 新バージョンの作成
v2を作成する場合：

1. **ディレクトリ作成**: `app/routers/v2/`
2. **統合ルーター**: `app/routers/v2/__init__.py`
3. **main.py登録**: `app.include_router(v2_router, prefix="/api/v2")`

## 使用される依存関係
- `fastapi.APIRouter`: ルーター統合機能
- `app.routers.v1.medii_q`: MediiQ機能モジュール

## ベストプラクティス

### インポート管理
- **エイリアス使用**: 名前衝突を避けるため `as router_name` を使用
- **明示的インポート**: 必要なオブジェクトのみをインポート

### タグ戦略
- **機能別分類**: 各機能ごとに適切なタグを設定
- **命名規則**: ケバブケース（`medii-q`）またはスネークケース（`medii_q`）で統一

### 拡張時の注意点
- **後方互換性**: 既存のエンドポイントに影響を与えない
- **テスト追加**: 新機能追加時には適切なテストを実装
- **ドキュメント更新**: 機能追加時にはドキュメントも併せて更新 