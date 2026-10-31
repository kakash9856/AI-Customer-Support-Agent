
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rag.document_loader import load_and_split_pdf

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "chroma_db"


def get_embeddings():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing in .env")

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )


def create_vector_store():

    print("Starting document indexing...")

    chunks = load_and_split_pdf()

    if not chunks:
        raise ValueError("No documents found.")

    embeddings = get_embeddings()

    DB_PATH.mkdir(parents=True, exist_ok=True)

    vector_store = Chroma(
        collection_name="customer_support",
        embedding_function=embeddings,
        persist_directory=str(DB_PATH)
    )

    # Add documents to existing database
    vector_store.add_documents(chunks)

    print("Documents successfully added to ChromaDB!")
    print("Total chunks indexed:", len(chunks))

    return vector_store


def get_vector_store():

    embeddings = get_embeddings()

    return Chroma(
        collection_name="customer_support",
        embedding_function=embeddings,
        persist_directory=str(DB_PATH)
    )
