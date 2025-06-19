# Schemas (schemas/medii_q.py)

## 概要
API リクエスト・レスポンスのデータモデルを定義するモジュールです。Pydantic を使用してデータの検証とシリアライゼーションを行います。

## データモデル

### Message
メッセージの基本構造を表すモデルです。

#### フィールド
- `role`: メッセージの役割（"user" または "assistant"）
- `content`: メッセージの内容（文字列）

#### 型注釈
```python
role: Literal["user", "assistant"]
content: str
```

### BaseRequest
API リクエストの基本構造を表すモデルです。

#### フィールド
- `thread_id`: スレッドID（文字列）
- `new_message`: 新しいメッセージ（文字列）
- `message_log`: メッセージ履歴のリスト（デフォルト: 空リスト）

#### 型注釈
```python
thread_id: str
new_message: str
message_log: list[Message] = []
```

### DbEvidenceRequirementsResponse
論文データベース検索の必要性判定結果を表すレスポンスモデルです。

#### フィールド
- `result`: 判定結果（"[DB_EVIDENCE:NEED]" または "[DB_EVIDENCE:NOT]"）

#### 型注釈
```python
result: str
```

### PubMedQueryResponse
PubMed検索クエリ生成結果を表すレスポンスモデルです。

#### フィールド
- `pubmed_query`: 生成されたPubMed検索クエリ（文字列）

#### 型注釈
```python
pubmed_query: str
```

### AssistantResponse
アシスタントの回答を表すレスポンスモデルです。

#### フィールド
- `response`: アシスタントの回答（文字列）

#### 型注釈
```python
response: str
```

## 使用例

### リクエストの作成
```python
from app.schemas.medii_q import BaseRequest, Message

# メッセージ履歴の作成
messages = [
    Message(role="user", content="こんにちは"),
    Message(role="assistant", content="こんにちは！何かお手伝いできることはありますか？")
]

# リクエストの作成
request = BaseRequest(
    thread_id="thread_123",
    new_message="医学について質問があります",
    message_log=messages
)
```

### レスポンスの作成
```python
from app.schemas.medii_q import PubMedQueryResponse

# PubMedクエリレスポンスの作成
response = PubMedQueryResponse(
    pubmed_query="(diabetes[MeSH Terms]) AND (treatment[Title/Abstract])"
)
```
