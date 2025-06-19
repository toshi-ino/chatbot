# Core Configuration (core/config.py)

## 概要
アプリケーション全体の設定を管理するモジュールです。環境変数から設定値を読み込み、アプリケーション全体で一貫した設定値を提供します。

## 主要なクラス

### Settings
Pydantic BaseSettingsを継承した設定クラスです。

#### アプリケーション基本設定
- `APP_NAME`: アプリケーション名（デフォルト: "MEDII AI PLATFORM"）
- `DEBUG`: デバッグモード（デフォルト: False）

#### OpenAI設定
- `OPENAI_API_KEY`: OpenAI APIキー（オプション）
- `DEFAULT_MODEL_NAME`: デフォルトのモデル名（デフォルト: "gpt-3.5-turbo"）
- `DEFAULT_TEMPERATURE`: デフォルトの温度設定（デフォルト: 0.7）

#### Pinecone設定
- `PINECONE_API_KEY`: Pinecone APIキー（オプション）
- `PINECONE_INDEX`: Pineconeインデックス名（オプション）

#### LangSmith設定
- `LANGSMITH_TRACING`: LangSmithトレーシングの有効/無効（デフォルト: False）
- `LANGSMITH_ENDPOINT`: LangSmithエンドポイント（オプション）
- `LANGSMITH_API_KEY`: LangSmith APIキー（オプション）
- `LANGSMITH_PROJECT`: LangSmithプロジェクト名（オプション）

#### 環境設定
- `ENVIRONMENT`: 環境名（オプション）

## 主要な関数

### get_settings()
- **目的**: 設定のシングルトンインスタンスを取得
- **戻り値**: `Settings` インスタンス
- **最適化**: `@lru_cache` デコレータにより初回取得後はキャッシュされる

## 設定の読み込み
- `.env` ファイルから環境変数を自動読み込み
- 大文字小文字を区別（case_sensitive = True）
- 定義されていない環境変数は無視（extra = "ignore"）

## 使用例
```python
from app.core.config import get_settings

settings = get_settings()
app_name = settings.APP_NAME
debug_mode = settings.DEBUG
```
