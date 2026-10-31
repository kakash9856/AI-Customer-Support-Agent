
import os
import hashlib
from pathlib import Path
from functools import lru_cache

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
        raise ValueError("GOOGLE_API_KEY missing in environment.")

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )


@lru_cache(maxsize=1)
def get_vector_store():

    print("Initializing ChromaDB...")

    DB_PATH.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name="customer_support",
        embedding_function=embeddings,
        persist_directory=str(DB_PATH)
    )

    print("Loading PDF and FAQ documents...")

    chunks = load_and_split_pdf()

    if not chunks:
        raise ValueError("No PDF or FAQ documents found.")

    # Generate stable IDs to prevent duplicate indexing
    document_ids = []

    for doc in chunks:
        source = doc.metadata.get("source", "")
        content = doc.page_content

        unique_text = f"{source}:{content}"

        doc_id = hashlib.sha256(
            unique_text.encode("utf-8")
        ).hexdigest()

        document_ids.append(doc_id)

    # Add documents to existing ChromaDB
    vector_store.add_documents(
        documents=chunks,
        ids=document_ids
    )

    print("PDF and FAQ indexing completed!")
    print("Documents processed:", len(chunks))

    return vector_store


def create_vector_store():
    return get_vector_store()
