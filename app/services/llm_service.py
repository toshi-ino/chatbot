from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage
from app.core.config import get_settings

settings = get_settings()

def get_llm():
    return ChatOpenAI(
        model=settings.MODEL_NAME,
        temperature=settings.TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY,
        streaming=True
    )

def create_chat_prompt(system_prompt: str, messages: list):
    prompt_messages = [SystemMessagePromptTemplate.from_template(system_prompt)]
    
    for msg in messages:
        if msg["role"] == "user":
            prompt_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            prompt_messages.append(AIMessage(content=msg["content"]))
    
    return ChatPromptTemplate.from_messages(prompt_messages) 