import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rag.document_loader import load_and_split_pdf

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "chroma_db"


def create_vector_store():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing in .env")

    chunks = load_and_split_pdf()

    if not chunks:
        raise ValueError("No text found in PDF files.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_PATH),
        collection_name="customer_support"
    )

    return vector_store


def get_vector_store():
    api_key = os.getenv("GOOGLE_API_KEY")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

    return Chroma(
        collection_name="customer_support",
        embedding_function=embeddings,
        persist_directory=str(DB_PATH)
    )