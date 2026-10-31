from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_pdf():
    documents_folder = (
        Path(__file__).parent.parent
        / "knowledge_base"
        / "documents"
    )

    pdf_files = list(documents_folder.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF found in knowledge_base/documents/"
        )

    documents = []

    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)
    return chunks