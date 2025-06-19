# MEDII AI Platform - Documentation

## 目次

1. [メインアプリケーション](./main.md) - FastAPIアプリケーションのエントリーポイント
2. [コア設定](./core.md) - アプリケーション設定の管理
3. [データモデル](./schemas.md) - APIリクエスト・レスポンスのスキーマ定義
4. [APIルーター](./router.md) - エンドポイントの定義と処理
5. [サービス層](./services.md) - ビジネスロジックとLLM処理

## アプリケーション概要

MEDII AI Platformは、医学的質問に対してAIを活用した回答を提供するプラットフォームです。PubMed検索クエリの生成、論文データベース検索の必要性判定、アシスタント回答の生成などの機能を提供します。

## アーキテクチャ

### 全体構成
```
app/
├── main.py              # アプリケーションエントリーポイント
├── core/
│   └── config.py        # 設定管理
├── routers/
│   └── medii_q.py       # APIエンドポイント定義
├── schemas/
│   └── medii_q.py       # データモデル定義
└── services/
    ├── llm_service.py   # LLM処理サービス
    └── langsmith_service.py # LangSmith連携サービス
```

### 技術スタック
- **Webフレームワーク**: FastAPI
- **LLM**: OpenAI GPT (LangChain経由)
- **プロンプト管理**: LangSmith
- **設定管理**: Pydantic Settings
- **データ検証**: Pydantic
- **環境変数**: python-dotenv

## 主要機能

### 1. PubMedクエリ生成
- ユーザーの質問から適切なPubMed検索クエリを自動生成
- LangSmithによるプロンプト管理
- トレーシング機能による処理追跡

### 2. 論文データベース検索判定
- 質問に対して論文検索が必要かどうかを自動判定
- `[DB_EVIDENCE:NEED]` または `[DB_EVIDENCE:NOT]` で結果を返却

### 3. アシスタント回答生成
- ストリーミング形式での回答生成
- リアルタイムでの応答配信
- メッセージ履歴を考慮した文脈理解

## API仕様

### エンドポイント一覧

| エンドポイント | メソッド | 説明 |
|---------------|----------|------|
| `/` | GET | 疎通確認 |
| `/api/pubmed-query` | POST | PubMedクエリ生成 |
| `/api/db-evidence-requirement` | POST | 論文検索必要性判定 |
| `/api/assistant-response` | POST | アシスタント回答生成（ストリーミング） |

### 共通リクエスト形式
```json
{
  "thread_id": "string",
  "new_message": "string",
  "message_log": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ]
}
```

## 設計思想

### 依存性注入
- サービス層では依存性注入パターンを使用
- テストやモック化が容易な設計

### エラーハンドリング
- 統一されたエラーレスポンス
- 適切なHTTPステータスコードの返却

### 拡張性
- 抽象基底クラスによる統一的な処理フロー
- 新しいAI機能の追加が容易

### 監視・トレーシング
- LangSmithによる処理トレーシング
- プロンプトの外部管理による運用効率化

