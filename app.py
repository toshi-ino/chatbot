import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.chains import RetrievalQA
from add_document import initialize_vectorstore
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "pr-sparkling-sigh-39")

openai_client = wrap_openai(OpenAI())

@traceable
def retriever(query: str):
    vectorstore = initialize_vectorstore()
    docs = vectorstore.similarity_search(query)
    return [doc.page_content for doc in docs]

@traceable
def rag(question: str):
    docs = retriever(question)
    callback = StreamlitCallbackHandler(st.container())

    system_message = """Answer the user's question using only the provided information below:\n\n{docs}""".format(
        docs="\n".join(docs)
    )

    llm = ChatOpenAI(
        model_name=os.environ["OPENAI_API_MODEL"],
        temperature=float(os.environ["OPENAI_API_TEMPERATURE"]),
        streaming=True,
        callbacks=[callback],
    )

    response = llm.invoke(system_message)
    return response

st.title("langchain-streamlit-app")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What's up?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = rag(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response.content})
