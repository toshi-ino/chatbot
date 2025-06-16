from langchain_openai import ChatOpenAI  # ← ここを修正
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

assist_judge_prompt = """
あなたは医学分野の専門家です。
ユーザーの会話履歴と最新メッセージを考慮し、「論文データベースの検索」が必要か否かを判定します。

- 医療に関連する質問でエビデンスが重要な場合は「[DB_EVIDENCE:NEED]」を返します。
- それ以外の場合は「[DB_EVIDENCE:NOT]」を返します。

判定結果以外は絶対に書かないでください。
"""

def judge_assist(new_message: str, message_log: list) -> str:
    messages = [SystemMessagePromptTemplate.from_template(assist_judge_prompt)]

    for log in message_log:
        role = log["role"]
        content = log["content"]
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=new_message))

    prompt = ChatPromptTemplate.from_messages(messages)

    chain = prompt | llm
    response = chain.invoke({})

    result_text = response.content.strip()

    return result_text

if __name__ == "__main__":
    new_message = "心房細動の患者に対する抗凝固療法の最新エビデンスを教えてください。"
    message_log = [
        {"role": "user", "content": "高血圧患者への降圧剤使用について教えてください。"},
        {"role": "assistant", "content": "[DB_EVIDENCE:NEED]"},
        {"role": "user", "content": "最近の研究で高血圧治療の新しい知見はありますか？"},
        {"role": "assistant", "content": "[DB_EVIDENCE:NEED]"}
    ]

    result = judge_assist(new_message, message_log)
    print(result)
