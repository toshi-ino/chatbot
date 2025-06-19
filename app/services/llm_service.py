from abc import ABC, abstractmethod
from typing import Optional

from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langsmith import traceable

from app.core.config import get_settings
from app.schemas.medii_q import Message
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

    @abstractmethod
    def get_prompt_template_and_model(self) -> tuple[str, Optional[str], Optional[float]]:
        pass

    def generate_response(self, message_log: list[Message], new_message: str) -> str:
        prompt_template, model_name, temperature = self.get_prompt_template_and_model()  # ←修正（括弧あり）

        llm = get_llm(model_name=model_name or settings.DEFAULT_MODEL_NAME, temperature=temperature or settings.DEFAULT_TEMPERATURE)
        message_log_dict = [{"role": msg.role, "content": msg.content} for msg in message_log]
        message_log_dict.append({"role": "user", "content": new_message})

        prompt = create_prompt_messages(prompt_template, message_log_dict)
        chain = prompt | llm
        response = chain.invoke({})
        return str(response.content).strip()

    async def generate_streaming_response(self, message_log: list[Message], new_message: str):
        prompt_template, model_name, temperature = self.get_prompt_template_and_model()
        llm = get_llm(model_name=model_name or settings.DEFAULT_MODEL_NAME, temperature=temperature or settings.DEFAULT_TEMPERATURE)

        message_log_dict = [{"role": msg.role, "content": msg.content} for msg in message_log]
        message_log_dict.append({"role": "user", "content": new_message})

        prompt = create_prompt_messages(prompt_template, message_log_dict)
        chain = prompt | llm

        async for chunk in chain.astream({}):
            if hasattr(chunk, "content") and chunk.content:
                yield str(chunk.content)


class PubMedQueryService(BaseLLMService):
    def get_prompt_template_and_model(self) -> tuple[str, Optional[str], Optional[float]]:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容を回答してください。
- ""
"""
        prompt_template, model_name, temperature = self.langsmith_service.get_prompt_and_model_from_langsmith(
            f"pubmed-query-prompt-{settings.ENVIRONMENT}", fallback_prompt
        )

        return prompt_template, model_name, temperature

    # NOTE：thread_idはlangsmithで計測するために引数に追加しています
    @traceable(name="PubMedQuery")
    def generate_pubmed_query(self, thread_id: str, message_log: list[Message], new_message: str) -> str:
        """
        メッセージからPubMedクエリを生成する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 生成されたPubMedクエリ
        """
        return self.generate_response(message_log, new_message)


class DbEvidenceRequirementService(BaseLLMService):
    def get_prompt_template_and_model(self) -> tuple[str, Optional[str], Optional[float]]:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容で回答してください。
- [DB_EVIDENCE:NOT]
"""
        prompt_template, model_name, temperature = self.langsmith_service.get_prompt_and_model_from_langsmith(
            f"db-evidence-requirement-prompt-{settings.ENVIRONMENT}", fallback_prompt
        )

        return prompt_template, model_name, temperature

    @traceable(name="DbEvidenceRequirement")
    def judge_db_evidence_requirement(self, thread_id: str, message_log: list[Message], new_message: str) -> str:
        """
        メッセージ履歴と新しいメッセージから論文データベース検索の必要性を判定する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 判定結果 ([DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT])
        """
        return self.generate_response(message_log, new_message)


class AssistantResponseService(BaseLLMService):
    def get_prompt_template_and_model(self) -> tuple[str, Optional[str], Optional[float]]:
        fallback_prompt = """
ユーザーの質問内容に関わらず、必ず以下の内容を回答してください。
- ""
"""
        prompt_template, model_name, temperature = self.langsmith_service.get_prompt_and_model_from_langsmith(
            f"assistant-response-prompt-{settings.ENVIRONMENT}", fallback_prompt
        )

        return prompt_template, model_name, temperature

    @traceable(name="AssistantResponse")
    async def generate_streaming_assistant_response(self, thread_id: str, message_log: list[Message], new_message: str):
        """
        アシスタント回答のストリーミングレスポンスを生成する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Yields:
            bytes: ストリーミングレスポンスのチャンク
        """
        async for chunk in self.generate_streaming_response(message_log, new_message):
            yield chunk
