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

load_dotenv()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def initialize_vectorstore():
    index_name = os.environ["PINECONE_INDEX"]
    embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])

    return  PineconeVectorStore(index_name=index_name, embedding=embeddings)


if __name__ == "__main__":
    file_path = sys.argv[1]
    loader = UnstructuredPDFLoader(file_path)
    raw_docs = loader.load()
    logger.info("Loaded %d documents", len(raw_docs))

    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    docs = text_splitter.split_documents(raw_docs)
    logger.info("Split %d documents", len(docs))

    api_key = os.environ["PINECONE_API_KEY"]
    # pc = Pinecone(api_key=api_key)

    index_name = os.environ["PINECONE_INDEX"]
    # index = pc.Index(name=index_name)

    embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])
    PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)
