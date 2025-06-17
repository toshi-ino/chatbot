from typing import List

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str

class BaseRequest(BaseModel):
    new_message: str
    message_log: List[Message]

class JudgeResponse(BaseModel):
    result: str  # [DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT] を返す

class PubMedQueryResponse(BaseModel):
    pubmed_query: str

class AssistantResponse(BaseModel):
    response: str
