# LangSmith Service (services/langsmith_service.py)

## 概要
LangSmithとの連携機能を提供するサービスです。プロンプトの取得やモデル設定の管理を行います。

## LangSmithServiceクラス

### 初期化
- 設定からLangSmith APIキーを取得
- APIキーが存在する場合のみクライアントを初期化

### 主要メソッド

#### get_prompt_and_model_from_langsmith(prompt_name, fallback_prompt)
LangSmithからプロンプトとモデル情報を取得する関数です。

- **引数**:
  - `prompt_name`: LangSmithのプロンプト名
  - `fallback_prompt`: 取得失敗時のフォールバックプロンプト

- **戻り値**: `tuple[str, Optional[str], Optional[float]]`
  - プロンプトテンプレート
  - モデル名（オプション）
  - 温度設定（オプション）

- **処理フロー**:
  1. LangSmithクライアントが存在するかチェック
  2. 指定されたプロンプト名でプロンプトを取得
  3. プロンプトテンプレートを抽出
  4. モデル情報（model_name, temperature）を抽出
  5. エラーが発生した場合はフォールバック値を返却

### エラーハンドリング
- LangSmithからの取得に失敗した場合、フォールバックプロンプトを使用
- クライアントが存在しない場合も同様にフォールバック処理

## 依存性注入

### get_langsmith_service()
LangSmithServiceのシングルトンインスタンスを取得する関数です。

- **戻り値**: `LangSmithService` インスタンス
- **最適化**: `@lru_cache` デコレータによりキャッシュされる

## 使用例

### LangSmithサービスの使用
```python
from app.services.langsmith_service import get_langsmith_service

# サービス取得
langsmith_service = get_langsmith_service()

# プロンプト取得
prompt, model, temp = langsmith_service.get_prompt_and_model_from_langsmith(
    "my-prompt", 
    "フォールバックプロンプト"
)
```

### プロンプト名の命名規則
各環境に対応したプロンプト名を使用します：
- `pubmed-query-prompt-{ENVIRONMENT}`
- `db-evidence-requirement-prompt-{ENVIRONMENT}`
- `assistant-response-prompt-{ENVIRONMENT}`

## 設定項目
LangSmithサービスで使用される環境変数：

```bash
# LangSmith設定
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_project_name
ENVIRONMENT=production
```

## 依存関係
- `langsmith`: LangSmithクライアント
- `app.core.config`: アプリケーション設定

## 利点
- **プロンプトの外部管理**: コードを変更せずにプロンプトを更新可能
- **バージョン管理**: LangSmithでプロンプトの履歴管理
- **A/Bテスト**: 異なるプロンプトの性能比較
- **フォールバック機能**: LangSmith接続失敗時の安全性

## 注意事項
- APIキーが設定されていない場合、常にフォールバックプロンプトが使用されます
- プロンプト取得に失敗した場合もフォールバック処理により処理が継続されます
- シングルトンパターンにより、アプリケーション全体で1つのインスタンスを共有します
