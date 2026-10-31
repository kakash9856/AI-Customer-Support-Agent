
from rag.vector_store import create_vector_store


if __name__ == "__main__":

    try:
        print("Indexing started...")

        create_vector_store()

        print("Indexing completed successfully!")

    except Exception as e:
        print("Indexing failed:", e)
