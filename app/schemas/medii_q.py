from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class BaseRequest(BaseModel):
    account_id: str
    thread_id: str
    new_message: str
    message_log: list[Message] = []


class DbEvidenceRequirementsResponse(BaseModel):
    result: str  # [DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT] を返す


class PubMedQueryResponse(BaseModel):
    pubmed_query: str


class AssistantResponse(BaseModel):
    response: str
