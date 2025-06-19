# LLM Service (services/llm_service.py)

## 概要
OpenAI GPTモデルを使用したLLM（大規模言語モデル）処理を行うサービスです。抽象基底クラスを使用して統一的な処理フローを提供し、各種AI機能を実装しています。

## 共通関数

### get_llm(model_name, temperature)
OpenAI ChatGPTのインスタンスを作成する関数です。

- **引数**:
  - `model_name`: 使用するモデル名（デフォルト: 設定値）
  - `temperature`: 生成の温度パラメータ（デフォルト: 設定値）
- **戻り値**: `ChatOpenAI` インスタンス

### create_prompt_messages(system_prompt, messages)
プロンプトメッセージリストを作成する関数です。

- **引数**:
  - `system_prompt`: システムプロンプト
  - `messages`: メッセージ履歴
- **戻り値**: `ChatPromptTemplate` インスタンス

## 抽象基底クラス

### BaseLLMService
すべてのLLMサービスの基底クラスです。

#### 初期化
- `langsmith_service`: LangSmithサービスの依存性注入（オプション）

#### 抽象メソッド
- `get_prompt_template_and_model()`: プロンプトテンプレートとモデル情報を取得

#### 実装メソッド
- `generate_response()`: 通常のレスポンス生成
- `generate_streaming_response()`: ストリーミングレスポンス生成

## 具象サービスクラス

### PubMedQueryService
PubMed検索クエリを生成するサービスです。

#### 主要メソッド
- `generate_pubmed_query(thread_id, message_log, new_message)`: PubMedクエリを生成
- **トレーシング**: `@traceable(name="PubMedQuery")`デコレータを使用

#### プロンプト取得
- LangSmithから`pubmed-query-prompt-{ENVIRONMENT}`を取得
- フォールバック: 空文字列を返すプロンプト

### DbEvidenceRequirementService
論文データベース検索の必要性を判定するサービスです。

#### 主要メソッド
- `judge_db_evidence_requirement(thread_id, message_log, new_message)`: 検索必要性を判定
- **トレーシング**: `@traceable(name="DbEvidenceRequirement")`デコレータを使用

#### プロンプト取得
- LangSmithから`db-evidence-requirement-prompt-{ENVIRONMENT}`を取得
- フォールバック: `[DB_EVIDENCE:NOT]`を返すプロンプト

### AssistantResponseService
アシスタント回答を生成するサービスです。

#### 主要メソッド
- `generate_streaming_assistant_response(thread_id, message_log, new_message)`: ストリーミング回答を生成
- **トレーシング**: `@traceable(name="AssistantResponse")`デコレータを使用

#### プロンプト取得
- LangSmithから`assistant-response-prompt-{ENVIRONMENT}`を取得
- フォールバック: 空文字列を返すプロンプト

## 使用例

### LLMサービスの使用
```python
from app.services.llm_service import PubMedQueryService
from app.services.langsmith_service import get_langsmith_service

# サービス初期化
langsmith_service = get_langsmith_service()
pubmed_service = PubMedQueryService(langsmith_service=langsmith_service)

# PubMedクエリ生成
query = pubmed_service.generate_pubmed_query(
    thread_id="thread_123",
    message_log=[],
    new_message="糖尿病の治療について"
)
```

## 依存関係
- `langchain`: OpenAI LLM処理とプロンプト管理
- `langsmith`: トレーシング機能
- `app.core.config`: アプリケーション設定
- `app.schemas.medii_q`: データモデル
- `app.services.langsmith_service`: LangSmith連携

## 設計パターン
- **抽象基底クラス**: 統一的な処理フローの提供
- **依存性注入**: テスト可能で拡張しやすい設計
- **Template Method**: プロンプト取得とLLM処理の分離
