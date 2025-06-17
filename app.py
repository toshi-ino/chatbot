# NOTE: RAGのデータをLangSmithでトレーシングする

import os
import uuid

import langsmith as ls
import openai
import streamlit as st
from dotenv import load_dotenv
from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai

from add_document import initialize_vectorstore

load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
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
    docs_with_scores = vectorstore.similarity_search_with_score(query)

    # スコア情報をLangSmithに記録
    run_tree = ls.get_current_run_tree()
    if run_tree:
        scores = [score for _, score in docs_with_scores]
        run_tree.outputs = {
            "documents": [doc.page_content for doc, _ in docs_with_scores],
            "scores": scores,
            "score_stats": {
                "min_score": min(scores) if scores else None,
                "max_score": max(scores) if scores else None,
                "avg_score": sum(scores) / len(scores) if scores else None,
            },
        }

    return [doc.page_content for doc, _ in docs_with_scores]


@traceable(name="RAG Chat Bot")
def rag(question: str, get_chat_history: bool = False):
    run_tree = ls.get_current_run_tree()
    if run_tree is None:
        metadata = {}
        session_name = "default_session"
    else:
        metadata = run_tree.extra.get("metadata", {}) if hasattr(run_tree, "extra") else {}
        session_name = run_tree.session_name if hasattr(run_tree, "session_name") else "default_session"
    session_id = metadata.get("session_id", "default_session")

    docs = retriever(question)

    if get_chat_history:
        messages = get_thread_history(session_id, session_name)
        messages.append({"role": "user", "content": question})
    else:
        messages = [{"role": "user", "content": question}]

    system_message = """Answer the user's question using only the provided information below:

{docs}""".format(docs="\n".join(docs))

    messages.insert(0, {"role": "system", "content": system_message})

    from typing import cast

    from openai.types.chat import ChatCompletionMessageParam

    chat_messages = cast(list[ChatCompletionMessageParam], [{"role": m["role"], "content": m["content"]} for m in messages])
    chat_completion = client.chat.completions.create(model="gpt-4", messages=chat_messages)

    return chat_completion.choices[0].message.content


def get_thread_history(thread_id: str, project_name: str):
    filter_string = f'and(in(metadata_key, ["session_id","conversation_id","thread_id"]), eq(metadata_value, "{thread_id}"))'
    runs = list(langsmith_client.list_runs(project_name=project_name, filter=filter_string, run_type="llm"))
    runs = sorted(runs, key=lambda run: run.start_time, reverse=True)
    if not runs:
        return []
    latest_run = runs[0]
    if not hasattr(latest_run, "inputs") or not hasattr(latest_run, "outputs"):
        return []
    inputs = getattr(latest_run, "inputs", {})
    outputs = getattr(latest_run, "outputs", {})
    return inputs.get("messages", []) + [outputs.get("choices", [{}])[0].get("message", {})]


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
        response = rag(prompt, get_chat_history=True)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
