
from rag.vector_store import create_vector_store

print("Creating vector database...")

try:
    db = create_vector_store()

    print("PDF successfully stored in ChromaDB!")

    results = db.similarity_search(
        "What are the customer support working hours?",
        k=3
    )

    print("\nSearch Results:")

    for result in results:
        print(result.page_content)
        print("Source:", result.metadata.get("source"))
        print("-" * 50)

except Exception as e:
    print("Error:", e)
