from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings

settings = get_settings()

def get_llm(model_name: str = settings.MODEL_NAME, temperature: float = settings.TEMPERATURE):
    return ChatOpenAI(
        model = model_name,
        temperature = temperature,
        openai_api_key = settings.OPENAI_API_KEY,
        streaming = True
    )

def create_chat_prompt(system_prompt: str, messages: list):
    prompt_messages = [SystemMessagePromptTemplate.from_template(system_prompt)]

    for msg in messages:
        if msg["role"] == "user":
            prompt_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            prompt_messages.append(AIMessage(content=msg["content"]))

    return ChatPromptTemplate.from_messages(prompt_messages)
