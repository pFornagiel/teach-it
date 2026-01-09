from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from loaders import load_file
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def build_vectorstore(file_paths: list[str]):
    docs = []

    for path in file_paths:
        docs.extend(load_file(path))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=OPENAI_API_KEY
    )

    return FAISS.from_documents(chunks, embeddings)
