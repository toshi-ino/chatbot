# chatbot
チャットボット

## 概要
LangChainとStreamlitを使用したRAG（Retrieval-Augmented Generation）チャットボットアプリケーションです。
PDFドキュメントをベクトル化してPineconeに保存し、質問に対して関連する情報を検索して回答を生成します。

## 機能
- PDFドキュメントの読み込みとベクトル化
- Pineconeを使用したベクトル検索
- OpenAI GPTモデルを使用した回答生成
- Streamlitによる対話型UI
- LangSmithによる観測とトレーシング

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
`.env`ファイルを作成し、以下の環境変数を設定してください：

```env
# OpenAI設定
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_MODEL=gpt-3.5-turbo
OPENAI_API_TEMPERATURE=0.7

# Pinecone設定
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=your_pinecone_index_name_here

# LangSmith設定（オプション - 観測とトレーシングのため）
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=chatbot-app
```

### 3. LangSmithの設定
LangSmithでの観測を有効にするには：

1. [LangSmith](https://smith.langchain.com/)にアカウントを作成
2. APIキーを取得
3. `.env`ファイルに`LANGSMITH_API_KEY`を設定
4. 必要に応じて`LANGCHAIN_PROJECT`名を変更

または、環境変数を直接設定することもできます：
```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="<your-langsmith-api-key>"
export LANGCHAIN_PROJECT="chatbot-app"
```

LangSmithが設定されると、以下の情報が自動的に記録されます：
- LLMの呼び出し履歴
- プロンプトと応答
- 実行時間とトークン使用量
- エラーログ
- チェーンの実行フロー
- `@traceable`デコレータで装飾された関数の実行トレース

## 使用方法

### 1. ドキュメントの追加
```bash
python add_document.py path/to/your/document.pdf
```

### 2. アプリケーションの起動
```bash
streamlit run app.py
```

### 3. チャットボットの使用
ブラウザでアプリケーションにアクセスし、質問を入力してください。
システムは関連するドキュメントを検索し、それに基づいて回答を生成します。

## LangSmithでの観測
アプリケーションが実行されると、LangSmithダッシュボードで以下を確認できます：
- 各会話セッションのトレース
- LLMの応答時間とコスト
- 検索クエリと結果
- エラーの詳細情報

プロジェクト名は環境変数`LANGCHAIN_PROJECT`で設定できます（デフォルト: "chatbot-app"）。
