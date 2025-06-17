from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langsmith import Client

# 環境変数を読み込み
load_dotenv()

# LangSmithクライアントを初期化
client = Client()

def pull_rag_system_prompt():
    """RAGシステム用プロンプトをLangSmithから取得"""
    try:
        prompt = client.pull_prompt("rag-system-prompt")
        print("✅ RAGシステムプロンプトを取得しました")
        return prompt
    except Exception as e:
        print(f"❌ プロンプトの取得に失敗しました: {e}")
        return None

def pull_rag_with_model():
    """RAGシステム（モデル付き）をLangSmithから取得"""
    try:
        chain = client.pull_prompt("rag-system-with-model", include_model=True)
        print("✅ RAGシステム（モデル付き）を取得しました")
        return chain
    except Exception as e:
        print(f"❌ プロンプト（モデル付き）の取得に失敗しました: {e}")
        return None

def pull_conversation_prompt():
    """会話継続用プロンプトをLangSmithから取得"""
    try:
        prompt = client.pull_prompt("rag-conversation-prompt")
        print("✅ 会話継続プロンプトを取得しました")
        return prompt
    except Exception as e:
        print(f"❌ 会話継続プロンプトの取得に失敗しました: {e}")
        return None

def test_rag_prompt():
    """RAGプロンプトのテスト実行"""
    print("\n🧪 RAGプロンプトのテスト実行...")

    # プロンプトを取得
    prompt = pull_rag_system_prompt()
    if not prompt:
        return

    # テスト用のコンテキストと質問
    test_context = """
    Python は1991年にGuido van Rossumによって開発されたプログラミング言語です。
    シンプルで読みやすい構文が特徴で、初心者にも学びやすい言語として人気があります。
    データサイエンス、ウェブ開発、自動化など様々な分野で使用されています。
    """

    test_question = "Pythonについて教えてください"

    # プロンプトを実行
    try:
        formatted_prompt = prompt.invoke({
            "context": test_context,
            "question": test_question
        })

        print("📝 フォーマット済みプロンプト:")
        print(formatted_prompt.to_string())

        # OpenAIモデルで実行
        model = ChatOpenAI(model="gpt-4o", temperature=0.1)
        response = model.invoke(formatted_prompt)

        print("\n🤖 AI応答:")
        print(response.content)

    except Exception as e:
        print(f"❌ プロンプトのテスト実行に失敗しました: {e}")

def test_conversation_prompt():
    """会話継続プロンプトのテスト実行"""
    print("\n🧪 会話継続プロンプトのテスト実行...")

    # プロンプトを取得
    prompt = pull_conversation_prompt()
    if not prompt:
        return

    # テスト用のデータ
    test_context = """
    機械学習は人工知能の一分野で、コンピュータがデータから自動的に学習する技術です。
    教師あり学習、教師なし学習、強化学習の3つの主要なタイプがあります。
    """

    test_chat_history = """
    ユーザー: AIについて教えてください
    アシスタント: AIは人工知能のことで、人間の知能を模倣する技術です。
    """

    test_question = "機械学習とAIの関係について詳しく説明してください"

    # プロンプトを実行
    try:
        formatted_prompt = prompt.invoke({
            "context": test_context,
            "chat_history": test_chat_history,
            "question": test_question
        })

        print("📝 フォーマット済みプロンプト:")
        print(formatted_prompt.to_string())

        # OpenAIモデルで実行
        model = ChatOpenAI(model="gpt-4o", temperature=0.1)
        response = model.invoke(formatted_prompt)

        print("\n🤖 AI応答:")
        print(response.content)

    except Exception as e:
        print(f"❌ 会話継続プロンプトのテスト実行に失敗しました: {e}")

def test_model_chain():
    """モデル付きチェーンのテスト実行"""
    print("\n🧪 モデル付きチェーンのテスト実行...")

    # チェーンを取得
    chain = pull_rag_with_model()
    if not chain:
        return

    # テスト用のデータ
    test_data = {
        "context": """
        LangSmithはLangChainが開発したLLMアプリケーションの開発・監視・評価プラットフォームです。
        プロンプトの管理、トレーシング、評価機能を提供しています。
        """,
        "question": "LangSmithの主な機能は何ですか？"
    }

    try:
        # チェーンを直接実行
        response = chain.invoke(test_data)

        print("🤖 チェーン実行結果:")
        print(response)

    except Exception as e:
        print(f"❌ チェーンの実行に失敗しました: {e}")

def list_available_prompts():
    """利用可能なプロンプト一覧を表示"""
    print("\n📋 利用可能なプロンプト一覧:")

    prompt_names = [
        "rag-system-prompt",
        "rag-system-with-model",
        "rag-conversation-prompt"
    ]

    for name in prompt_names:
        try:
            prompt = client.pull_prompt(name)
            print(f"  ✅ {name} - 利用可能")
        except Exception as e:
            print(f"  ❌ {name} - 取得失敗: {e}")

def main():
    """メイン実行関数"""
    print("🔄 LangSmithからプロンプトを取得してテストします...\n")

    # 利用可能なプロンプトを確認
    list_available_prompts()

    # 各プロンプトをテスト
    test_rag_prompt()
    test_conversation_prompt()
    test_model_chain()

    print("\n✨ プロンプトのテストが完了しました！")

if __name__ == "__main__":
    main()
