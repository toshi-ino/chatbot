# プロンプトをLangSmithにアップロードする処理

import os
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# LangSmithクライアントを初期化
client = Client()

def upload_rag_system_prompt():
    """RAGシステム用のプロンプトをLangSmithにアップロード"""
    
    # RAGシステム用のプロンプトテンプレートを作成
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", """あなたは親切で知識豊富なアシスタントです。
以下の情報のみを使用してユーザーの質問に答えてください：

{context}

重要な注意事項：
- 提供された情報のみを使用して回答してください
- 情報が不十分な場合は、「提供された情報では回答できません」と伝えてください
- 推測や憶測は避けてください
- 回答は日本語で行ってください"""),
        ("human", "{question}")
    ])
    
    try:
        # プロンプトをLangSmithにアップロード
        url = client.push_prompt("rag-system-prompt", object=rag_prompt)
        print(f"✅ RAGシステムプロンプトをアップロードしました: {url}")
        return url
    except Exception as e:
        print(f"❌ プロンプトのアップロードに失敗しました: {e}")
        return None

def upload_rag_with_model():
    """RAGシステム用のプロンプト（モデル設定付き）をLangSmithにアップロード"""
    
    # プロンプトテンプレートを作成
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", """あなたは親切で知識豊富なアシスタントです。
以下の情報のみを使用してユーザーの質問に答えてください：

{context}

重要な注意事項：
- 提供された情報のみを使用して回答してください
- 情報が不十分な場合は、「提供された情報では回答できません」と伝えてください
- 推測や憶測は避けてください
- 回答は日本語で行ってください"""),
        ("human", "{question}")
    ])
    
    # モデルを設定
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1000
    )
    
    # プロンプトとモデルを組み合わせたチェーンを作成
    chain = rag_prompt | model
    
    try:
        # チェーンをLangSmithにアップロード
        url = client.push_prompt("rag-system-with-model", object=chain)
        print(f"✅ RAGシステム（モデル付き）をアップロードしました: {url}")
        return url
    except Exception as e:
        print(f"❌ プロンプト（モデル付き）のアップロードに失敗しました: {e}")
        return None

def upload_conversation_prompt():
    """会話継続用のプロンプトをLangSmithにアップロード"""
    
    conversation_prompt = ChatPromptTemplate.from_messages([
        ("system", """あなたは親切で知識豊富なアシスタントです。
以下の情報と会話履歴を参考にして、ユーザーの質問に答えてください：

参考情報：
{context}

会話履歴：
{chat_history}

重要な注意事項：
- 提供された情報と会話履歴を活用して回答してください
- 情報が不十分な場合は、「提供された情報では回答できません」と伝えてください
- 会話の文脈を考慮して自然な対話を心がけてください
- 回答は日本語で行ってください"""),
        ("human", "{question}")
    ])
    
    try:
        url = client.push_prompt("rag-conversation-prompt", object=conversation_prompt)
        print(f"✅ 会話継続プロンプトをアップロードしました: {url}")
        return url
    except Exception as e:
        print(f"❌ 会話継続プロンプトのアップロードに失敗しました: {e}")
        return None

def list_uploaded_prompts():
    """アップロード済みのプロンプト一覧を表示"""
    try:
        prompts = list(client.list_prompts())
        print("\n📋 アップロード済みプロンプト一覧:")
        for prompt in prompts:
            print(f"  - {prompt.name} (作成日: {prompt.created_at})")
    except Exception as e:
        print(f"❌ プロンプト一覧の取得に失敗しました: {e}")

def main():
    """メイン実行関数"""
    print("🚀 LangSmithにプロンプトをアップロードします...\n")
    
    # 各プロンプトをアップロード
    upload_rag_system_prompt()
    upload_rag_with_model()
    upload_conversation_prompt()
    
    print("\n" + "="*50)
    
    # アップロード済みプロンプトを表示
    list_uploaded_prompts()
    
    print("\n✨ プロンプトのアップロードが完了しました！")

if __name__ == "__main__":
    main() 