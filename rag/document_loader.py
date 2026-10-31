
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_pdf():

    base_dir = Path(__file__).parent.parent

    documents_folder = (
        base_dir / "knowledge_base" / "documents"
    )

    faq_file = (
        base_dir / "knowledge_base" / "faqs.txt"
    )

    documents = []

    # Step 1: Load PDF files
    pdf_files = list(documents_folder.glob("*.pdf"))

    for pdf_path in pdf_files:
        print(f"Loading PDF: {pdf_path.name}")

        loader = PyPDFLoader(str(pdf_path))
        documents.extend(loader.load())

    # Step 2: Load FAQ text file
    if faq_file.exists():
        print("Loading FAQ file:", faq_file.name)

        loader = TextLoader(
            str(faq_file),
            encoding="utf-8"
        )

        documents.extend(loader.load())

    else:
        print("WARNING: faqs.txt not found!")

    # Step 3: Check documents
    if not documents:
        raise ValueError(
            "No PDF or FAQ documents found in knowledge_base."
        )

    print("Total documents loaded:", len(documents))

    # Step 4: Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    print("Total chunks created:", len(chunks))

    return chunks
