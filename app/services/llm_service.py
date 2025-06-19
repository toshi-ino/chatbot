from abc import ABC, abstractmethod

from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.schemas.schemas import Message
from app.services.langsmith_service import get_langsmith_service

settings = get_settings()


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


class BaseLLMService(ABC):
    """プロンプトベースのLLM処理を行う抽象基底クラス"""

    def __init__(self, langsmith_service=None):
        # 依存性注入を受け入れる（フォールバック付き）
        self.langsmith_service = langsmith_service or get_langsmith_service()

    @property
    @abstractmethod
    def prompt_template(self) -> str:
        pass

    def generate_response(self, message_log: list[Message], new_message: str, model_name: str, temperature: float) -> str:
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
        return self.langsmith_service.get_prompt_from_langsmith(f"pubmed-query-prompt-{settings.ENVIRONMENT}", fallback_prompt)

    def generate_pubmed_query(self, message_log: list[Message], new_message: str) -> str:
        """
        メッセージからPubMedクエリを生成する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 生成されたPubMedクエリ
        """
        return self.generate_response(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7)


class DbEvidenceRequirementsService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容で回答してください。
- [DB_EVIDENCE:NOT]
"""
        return self.langsmith_service.get_prompt_from_langsmith(f"db-evidence-requirement-prompt-{settings.ENVIRONMENT}", fallback_prompt)

    def judge_db_evidence_requirement(self, message_log: list[Message], new_message: str) -> str:
        """
        メッセージ履歴と新しいメッセージから論文データベース検索の必要性を判定する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 判定結果 ([DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT])
        """
        return self.generate_response(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7)


class AssistantResponseService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容を回答してください。
- ""
"""
        return self.langsmith_service.get_prompt_from_langsmith(f"assistant-response-prompt-{settings.ENVIRONMENT}", fallback_prompt)

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
