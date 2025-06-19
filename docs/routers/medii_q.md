# Router (routers/medii_q.py)

## 概要
MEDII Q関連のAPIエンドポイントを定義するルーターモジュールです。PubMedクエリ生成、論文データベース検索の必要性判定、アシスタント回答生成の3つの主要機能を提供します。

## 依存性注入
- `LangSmithService`: LangSmithとの連携機能を提供
- ルーター内で直接依存性注入するとエラーが発生するため、`Depends`を別途定義

## APIエンドポイント

### POST /api/pubmed-query
PubMedの検索クエリを生成するエンドポイントです。

#### リクエスト
- **型**: `BaseRequest`
- **パラメータ**:
  - `thread_id`: スレッドID
  - `new_message`: 新しいメッセージ
  - `message_log`: メッセージ履歴

#### レスポンス
- **型**: `PubMedQueryResponse`
- **内容**: 生成されたPubMed検索クエリ

#### 処理フロー
1. `PubMedQueryService`のインスタンスを作成
2. メッセージ履歴と新しいメッセージからPubMedクエリを生成
3. 生成されたクエリをレスポンスとして返却

#### エラーハンドリング
- 処理中に例外が発生した場合、HTTP 500エラーを返却

### POST /api/db-evidence-requirement
論文データベース検索の必要性を判定するエンドポイントです。

#### リクエスト
- **型**: `BaseRequest`
- **パラメータ**:
  - `thread_id`: スレッドID
  - `new_message`: 新しいメッセージ
  - `message_log`: メッセージ履歴

#### レスポンス
- **型**: `DbEvidenceRequirementsResponse`
- **内容**: 判定結果（"[DB_EVIDENCE:NEED]" または "[DB_EVIDENCE:NOT]"）

#### 処理フロー
1. `DbEvidenceRequirementService`のインスタンスを作成
2. メッセージ履歴と新しいメッセージから論文検索の必要性を判定
3. 判定結果をレスポンスとして返却

#### エラーハンドリング
- 処理中に例外が発生した場合、HTTP 500エラーを返却

### POST /api/assistant-response
ストリーミングレスポンスを生成するエンドポイントです。

#### リクエスト
- **型**: `BaseRequest`
- **パラメータ**:
  - `thread_id`: スレッドID
  - `new_message`: 新しいメッセージ
  - `message_log`: メッセージ履歴

#### レスポンス
- **型**: `StreamingResponse`
- **メディアタイプ**: "text/plain"
- **内容**: アシスタントの回答をストリーミング形式で配信

#### 処理フロー
1. `AssistantResponseService`のインスタンスを作成
2. メッセージ履歴と新しいメッセージからストリーミングレスポンスを生成
3. ストリーミング形式でレスポンスを返却

#### エラーハンドリング
- 処理中に例外が発生した場合、HTTP 500エラーを返却

## 使用される依存関係
- `fastapi`: WebフレームワークとHTTPレスポンス
- `app.schemas.medii_q`: リクエスト・レスポンスモデル
- `app.services.langsmith_service`: LangSmith連携サービス
- `app.services.llm_service`: LLM処理サービス

## 注意事項
- 全てのエンドポイントで統一したエラーハンドリングを実装
- LangSmithサービスは依存性注入により提供される
- ストリーミングレスポンスは非同期処理で実装
