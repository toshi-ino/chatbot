import streamlit as st
import openai
from langsmith import traceable, Client
from langsmith.wrappers import wrap_openai
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
import os
import uuid
from dotenv import load_dotenv
from langsmith.utils import LangSmithConflictError

load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

client = wrap_openai(openai.OpenAI())
langsmith_client = Client()

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

session_id = st.session_state["thread_id"]

langsmith_extra = {"metadata": {"session_id": session_id}}

@traceable(name="Chat Bot")
def chat_pipeline(inputs: dict) -> dict:
    question = inputs["question"]
    messages = [{"role": "user", "content": question}]

    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return {"answer": chat_completion.choices[0].message.content.strip()}

# Evaluatorの設定
def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        model="openai:gpt-4o",
        feedback_key="correctness",
    )
    return evaluator(inputs=inputs, outputs=outputs, reference_outputs=reference_outputs)

# Streamlit UI
st.title("LangSmith Evaluation Chatbot")

prompt = st.chat_input("メッセージを入力してください")

if prompt:
    st.session_state.setdefault("messages", []).append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    inputs = {"question": prompt}
    response_dict = chat_pipeline(inputs)
    response = response_dict["answer"]

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Evaluationを実施
try:
    dataset = langsmith_client.create_dataset(
        dataset_name="Chatbot Evaluation Dataset v4",
        description="Dataset for chatbot evaluation."
    )
except LangSmithConflictError:
    dataset = langsmith_client.read_dataset(dataset_name="Chatbot Evaluation Dataset")

examples = [{
    "inputs": {"question": "What is the capital of France?"},
    "outputs": {"answer": "The capital of France is Paris."}
}]
langsmith_client.create_examples(dataset_id=dataset.id, examples=examples)

if st.button("Run Evaluation"):
    experiment_results = langsmith_client.evaluate(
        chat_pipeline,
        data="Chatbot Evaluation Dataset",
        evaluators=[correctness_evaluator],
        experiment_prefix="chatbot-eval"
    )

    st.write("Evaluation completed. Check LangSmith dashboard for results.")