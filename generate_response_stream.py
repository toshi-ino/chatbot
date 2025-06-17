import os

from dotenv import load_dotenv
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()

# OpenAIのChatモデルを設定（ストリーミングを有効化）
llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True, api_key=SecretStr(os.getenv("OPENAI_API_KEY", "")))


def stream_assistant_response(prompt_template: str, new_message: str, message_log: list):
    messages = [SystemMessagePromptTemplate.from_template(prompt_template)]

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

    for chunk in chain.stream({}):
        content = chunk.content
        if content:
            yield content


# プロンプト内の {PMID} は {{PMID}} にエスケープします。
prompt = """
あなたは医学分野の専門家です。ユーザーの医療に関する質問に対して、科学的根拠に基づいた回答を提供します。
回答は日本語で提供し、まず結論と要約を述べ、その後に文献に基づく治療方針の概要を示してください。
臨床データ等の根拠を示し、PMIDを含める場合は必ず「PMID:{{PMID}}」の形式にすること。
最後に必ず次を記載する：
- 本回答は情報提供を目的としているため、最終的な診断や治療方針の決定は主治医の判断に委ねられます。
- 新規治療薬や治療法に関するエビデンスは日々更新されるため、最新の文献・ガイドラインに基づいた判断と定期的な再評価が必要となります。
"""

if __name__ == "__main__":
    new_message = "高齢の心房細動患者に対する抗凝固療法の最新エビデンスを教えてください。"
    message_log = [
        {"role": "user", "content": "心房細動患者の出血リスク管理について教えてください。"},
        {"role": "assistant", "content": "心房細動患者の出血リスク管理にはCHA₂DS₂-VAScスコアやHAS-BLEDスコアが使用されます。[DB_EVIDENCE:NEED]"},
    ]

    print("LLMの応答（ストリーミング）:")
    for chunk in stream_assistant_response(prompt, new_message, message_log):
        print(chunk, end="", flush=True)
