import os
import sys
import logging

import pinecone
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langsmith import traceable

load_dotenv()

# LangSmithの設定（公式ドキュメントに従った環境変数名）
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "chatbot-app")
# LANGSMITH_API_KEYは.envファイルから読み込まれる

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

@traceable(name="initialize_vectorstore")
def initialize_vectorstore():
    index_name = os.environ["PINECONE_INDEX"]
    embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])

    return PineconeVectorStore(index_name=index_name, embedding=embeddings)

@traceable(name="load_and_split_documents")
def load_and_split_documents(file_path: str):
    """PDFファイルを読み込み、チャンクに分割する"""
    loader = UnstructuredPDFLoader(file_path)
    raw_docs = loader.load()
    logger.info("Loaded %d documents", len(raw_docs))

    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    docs = text_splitter.split_documents(raw_docs)
    logger.info("Split %d documents", len(docs))
    
    return docs

@traceable(name="add_documents_to_vectorstore")
def add_documents_to_vectorstore(docs, index_name: str):
    """ドキュメントをベクトルストアに追加する"""
    embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])
    PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)
    logger.info("Added %d documents to vectorstore", len(docs))

if __name__ == "__main__":
    file_path = sys.argv[1]
    
    # ドキュメントの読み込みと分割
    docs = load_and_split_documents(file_path)
    
    # ベクトルストアへの追加
    index_name = os.environ["PINECONE_INDEX"]
    add_documents_to_vectorstore(docs, index_name)
