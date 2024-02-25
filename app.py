import os

import streamlit as st
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.chains import RetrievalQA
from add_document import initialize_vectorstore

load_dotenv()

def create_qa_chain():
    callback = StreamlitCallbackHandler(st.container())

    llm = ChatOpenAI(
        model_name=os.environ["OPENAI_API_MODEL"],
        temperature=float(os.environ["OPENAI_API_TEMPERATURE"]),
        streaming=True,
        callbacks=[callback],
        )

    vectorstore = initialize_vectorstore()

    qa_chain = RetrievalQA.from_llm(llm=llm, retriever=vectorstore.as_retriever())

    return qa_chain

if "agent_chain" not in st.session_state:
    st.session_state.agent_chain = create_qa_chain()

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
        qa_chain = create_qa_chain()
        response = qa_chain.invoke(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response["result"]})