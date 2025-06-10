# NOTE: RAGのデータをLangSmithでトレーシングする

import streamlit as st
import openai
from langsmith import traceable, Client
import langsmith as ls
from langsmith.wrappers import wrap_openai
import os
import uuid
from dotenv import load_dotenv
from add_document import initialize_vectorstore

load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "project-with-threads")

client = wrap_openai(openai.OpenAI())
langsmith_client = Client()

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

session_id = st.session_state["thread_id"]
langsmith_extra = {"metadata": {"session_id": session_id}}

@traceable(run_type="retriever")
def retriever(query: str):
    vectorstore = initialize_vectorstore()
    docs = vectorstore.similarity_search(query)
    return [doc.page_content for doc in docs]

@traceable(name="RAG Chat Bot")
def rag(question: str, get_chat_history: bool = False):
    run_tree = ls.get_current_run_tree()
    metadata = run_tree.extra.get("metadata", {})
    session_id = metadata.get("session_id", "default_session")

    docs = retriever(question)

    if get_chat_history:
        messages = get_thread_history(session_id, run_tree.session_name)
        messages.append({"role": "user", "content": question})
    else:
        messages = [{"role": "user", "content": question}]

    system_message = """Answer the user's question using only the provided information below:

{docs}""".format(docs="\n".join(docs))

    messages.insert(0, {"role": "system", "content": system_message})

    chat_completion = client.chat.completions.create(
        model="gpt-4o", messages=messages
    )

    return chat_completion.choices[0].message.content

def get_thread_history(thread_id: str, project_name: str):
    filter_string = f'and(in(metadata_key, ["session_id","conversation_id","thread_id"]), eq(metadata_value, "{thread_id}"))'
    runs = [r for r in langsmith_client.list_runs(project_name=project_name, filter=filter_string, run_type="llm")]
    runs = sorted(runs, key=lambda run: run.start_time, reverse=True)
    if not runs:
        return []
    latest_run = runs[0]
    return latest_run.inputs['messages'] + [latest_run.outputs['choices'][0]['message']]

st.title("RAG Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("メッセージを入力してください")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = rag(
            prompt,
            get_chat_history=True,
            langsmith_extra=langsmith_extra
        )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})