from abc import ABC, abstractmethod

from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langsmith import Client

from app.api.schemas.schemas import Message
from app.core.config import get_settings

settings = get_settings()

# LangSmithクライアントを初期化（APIキーがある場合のみ）
client = None
if settings.LANGSMITH_API_KEY:
    client = Client(api_key=settings.LANGSMITH_API_KEY)


def get_llm(model_name: str = settings.DEFAULT_MODEL_NAME, temperature: float = settings.DEFAULT_TEMPERATURE):
    return ChatOpenAI(model=model_name, temperature=temperature, streaming=True)


def create_prompt_messages(system_prompt: str, messages: list):
    prompt_messages: list = [SystemMessage(content=system_prompt)]

    for msg in messages:
        if msg["role"] == "user":
            prompt_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            prompt_messages.append(AIMessage(content=msg["content"]))

    return ChatPromptTemplate.from_messages(prompt_messages)


def get_prompt_from_langsmith(prompt_name: str, fallback_prompt: str) -> str:
    """
    LangSmithからプロンプトを取得する共通メソッド

    Args:
        prompt_name: LangSmithのプロンプト名
        fallback_prompt: 取得に失敗した場合のフォールバックプロンプト

    Returns:
        str: プロンプトテンプレート文字列
    """
    if client is not None:
        try:
            prompt = client.pull_prompt(prompt_name)

            if hasattr(prompt, "messages") and prompt.messages:
                first_message = prompt.messages[0]
                template = getattr(first_message, "prompt", None)

                if template and hasattr(template, "template"):
                    return template.template

            print(f"LangSmithからプロンプト({prompt_name})を取得できませんでした。")
            return fallback_prompt

        except Exception as e:
            print(f"LangSmithからプロンプト({prompt_name})取得時にエラーが発生しました。: {e}")
            return fallback_prompt

    print("LangsmithのClientが存在しません。")
    return fallback_prompt


class BaseLLMService(ABC):
    """プロンプトベースのLLM処理を行う抽象基底クラス"""

    @property
    @abstractmethod
    def prompt_template(self) -> str:
        pass

    def process_message(self, message_log: list[Message], new_message: str, model_name: str, temperature: float) -> str:
        llm = get_llm(model_name=model_name, temperature=temperature)
        message_log_dict = [{"role": msg.role, "content": msg.content} for msg in message_log]
        message_log_dict.append({"role": "user", "content": new_message})

        prompt = create_prompt_messages(self.prompt_template, message_log_dict)
        chain = prompt | llm
        response = chain.invoke({})
        return str(response.content).strip()

    async def generate_streaming_response(self, message_log: list[Message], new_message: str, model_name: str, temperature: float):
        """
        メッセージからストリーミングレスポンスを生成する汎用メソッド

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ
            model_name: 使用するLLMモデル名（デフォルト: gpt-4o-mini）
            temperature: LLMの温度パラメータ（デフォルト: 0.7）

        Yields:
            bytes: ストリーミングレスポンスのチャンク
        """
        llm = get_llm(model_name=model_name, temperature=temperature)

        # メッセージリストを作成
        message_log_dict = [{"role": msg.role, "content": msg.content} for msg in message_log]
        message_log_dict.append({"role": "user", "content": new_message})

        prompt = create_prompt_messages(self.prompt_template, message_log_dict)
        chain = prompt | llm

        async for chunk in chain.astream({}):
            if hasattr(chunk, "content") and chunk.content:
                yield str(chunk.content).encode("utf-8")


class PubMedQueryService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容を回答してください。
- ""
"""
        return get_prompt_from_langsmith(f"pubmed-query-prompt-{settings.ENVIRONMENT}", fallback_prompt)

    def generate_pubmed_query(self, message_log: list[Message], new_message: str) -> str:
        """
        メッセージからPubMedクエリを生成する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 生成されたPubMedクエリ
        """
        return self.process_message(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7)


class DbEvidenceRequirementsService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容で回答してください。
- [DB_EVIDENCE:NOT]
"""
        return get_prompt_from_langsmith(f"db-evidence-requirement-prompt-{settings.ENVIRONMENT}", fallback_prompt)

    def judge_db_evidence_requirement(self, message_log: list[Message], new_message: str) -> str:
        """
        メッセージ履歴と新しいメッセージから論文データベース検索の必要性を判定する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 判定結果 ([DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT])
        """
        return self.process_message(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7)


class AssistantResponseService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容を回答してください。
- ""
"""
        return get_prompt_from_langsmith(f"assistant-response-prompt-{settings.ENVIRONMENT}", fallback_prompt)

    async def generate_streaming_assistant_response(self, message_log: list[Message], new_message: str):
        """
        アシスタント回答のストリーミングレスポンスを生成する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Yields:
            bytes: ストリーミングレスポンスのチャンク
        """
        async for chunk in self.generate_streaming_response(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7):
            yield chunk
