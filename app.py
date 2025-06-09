# import os

# import streamlit as st
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_community.callbacks import StreamlitCallbackHandler
# from add_document import initialize_vectorstore
# from langsmith import traceable
# from langsmith.wrappers import wrap_openai
# from openai import OpenAI
# import uuid

# load_dotenv()

# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
# os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
# os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "pr-sparkling-sigh-39")

# openai_client = wrap_openai(OpenAI())

# @traceable(run_type="retriever")
# def retriever(query: str, langsmith_extra):
#     vectorstore = initialize_vectorstore()
#     docs = vectorstore.similarity_search(query)
#     return [doc.page_content for doc in docs]

# @traceable
# def rag(question: str, langsmith_extra):
#     docs = retriever(question, langsmith_extra)
#     callback = StreamlitCallbackHandler(st.container())

#     system_message = """Answer the user's question using only the provided information below:\n\n{docs}""".format(
#         docs="\n".join(docs)
#     )

#     llm = ChatOpenAI(
#         model_name=os.environ["OPENAI_API_MODEL"],
#         temperature=float(os.environ["OPENAI_API_TEMPERATURE"]),
#         streaming=True,
#         callbacks=[callback],
#     )

#     response = llm.invoke(system_message)  # langsmith_extraをここから削除
#     return response

# st.title("langchain-streamlit-app")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Thread ID management
# thread_id = st.session_state.get("thread_id")
# if not thread_id:
#     thread_id = str(uuid.uuid4())
#     st.session_state["thread_id"] = thread_id

# # Include session_id in metadata for LangSmith threads
# langsmith_extra = {"metadata": {"session_id": thread_id}}

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# prompt = st.chat_input("What's up?")

# if prompt:
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         response = rag(prompt, langsmith_extra)

#     st.session_state.messages.append({"role": "assistant", "content": response.content})


import streamlit as st
import openai
from langsmith import traceable, Client
import langsmith as ls
from langsmith.wrappers import wrap_openai
import os
import uuid
from dotenv import load_dotenv

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

def get_thread_history(thread_id: str, project_name: str):
    filter_string = f'and(in(metadata_key, ["session_id","conversation_id","thread_id"]), eq(metadata_value, "{thread_id}"))'
    runs = [r for r in langsmith_client.list_runs(project_name=project_name, filter=filter_string, run_type="llm")]
    runs = sorted(runs, key=lambda run: run.start_time, reverse=True)
    if not runs:
        return []
    latest_run = runs[0]
    return latest_run.inputs['messages'] + [latest_run.outputs['choices'][0]['message']]

@traceable(name="Chat Bot")
def chat_pipeline(question: str, get_chat_history: bool = False):
    run_tree = ls.get_current_run_tree()
    metadata = run_tree.extra.get("metadata", {})
    session_id = metadata.get("session_id", "default_session")

    if get_chat_history:
        messages = get_thread_history(session_id, run_tree.session_name) + [{"role": "user", "content": question}]
    else:
        messages = [{"role": "user", "content": question}]

    chat_completion = client.chat.completions.create(
        model="gpt-4o", messages=messages
    )
    return chat_completion.choices[0].message.content


st.title("Chatbot")

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
        response = chat_pipeline(
            prompt,
            langsmith_extra=langsmith_extra,
            get_chat_history=True
        )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


