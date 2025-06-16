from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAIのChatモデルを設定
llm = ChatOpenAI(
    model="gpt-4o-mini",       # モデル指定（GPT-4o）
    temperature=0,        # 決定的出力を得るため
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# PubMedクエリ生成用のプロンプト（提示された内容を使用）
pubmed_query_generate_prompt = """
あなたは医学分野に精通した検索エキスパートです。ユーザーの医療に関する質問からPubMed検索に最適なクエリを生成してください。
出力は指定の書式のみとし、それ以外の説明・注釈・空行・コードブロック・装飾は一切書かないでください。

✅ クエリ作成ルール
1. PICO抽出:
  - Population / Intervention / Comparison / Outcomeを質問文から抽出。
  - 不明または存在しない要素は省略するかワイルドカード*を代用。
2. 語彙とタグ付け:
  - 各PICO要素に必ず1つ以上の検索語を割り当てる。
  - 優先順位: "XXXXX"[MeSH Terms] > XXXXX[Title/Abstract]またはXXXXX[TIAB]。
  - All Fieldsは禁止。
3. 要素間の結合:
  - 異なるPICO要素はANDで結合。
4. フィルタリング:
  - 研究デザインや出版タイプを必要に応じて追加（例: "Randomized Controlled Trial"[Publication Type]）。
5. 出力はクエリのみ。
"""

def generate_pubmed_query(new_message: str, message_log: list) -> str:
    """
    医療関連質問からPubMed検索クエリを生成する関数

    Args:
        new_message (str): ユーザーの最新質問文
        message_log (list): 過去の会話履歴（role, contentのdictリスト）

    Returns:
        str: 生成されたPubMed検索クエリ
    """

    # システムプロンプトを設定
    messages = [SystemMessagePromptTemplate.from_template(pubmed_query_generate_prompt)]

    # 会話履歴を追加
    for log in message_log:
        role = log["role"]
        content = log["content"]
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    # 最新のユーザーメッセージを追加
    messages.append(HumanMessage(content=new_message))

    # プロンプトを構成
    prompt = ChatPromptTemplate.from_messages(messages)

    # LLMを呼び出してPubMedクエリを取得
    chain = prompt | llm
    response = chain.invoke({})

    # 結果テキストを整形
    pubmed_query = response.content.strip()

    return pubmed_query

# 実行例
if __name__ == "__main__":
    new_message = "高齢の心房細動患者に対する最適な抗凝固療法は何ですか？"
    message_log = [
        {"role": "user", "content": "心房細動患者の出血リスク管理について教えてください。"},
        {"role": "assistant", "content": "[DB_EVIDENCE:NEED]"},
    ]

    pubmed_query = generate_pubmed_query(new_message, message_log)
    print("生成されたPubMedクエリ:")
    print(pubmed_query)
