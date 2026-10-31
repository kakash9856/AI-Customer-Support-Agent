
from rag.vector_store import get_vector_store
from config import llm


def ask_question(question, chat_history=None, intent="general_query"):

    print("1. Searching Knowledge Base...")
    print("Detected Intent:", intent)

    vector_store = get_vector_store()

    # Search using the original customer question
    search_query = question

    docs = vector_store.similarity_search(search_query, k=4)

    print("2. Retrieved documents:", len(docs))

    # DEBUG: Display retrieved document content
    for i, doc in enumerate(docs):
        print(f"\nDocument {i + 1}:")
        print(doc.page_content)

    if not docs:
        return "No relevant information found in the knowledge base."

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    history = ""

    if chat_history:
        history = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in chat_history[-6:]
        )

    prompt = f"""
You are a professional customer support assistant.

Customer Intent: {intent}

Instructions:
1. Answer according to the detected customer intent.
2. Use only the provided knowledge base.
3. Do not invent refund, delivery or cancellation policies.
4. Use previous conversation when relevant.
5. If information is unavailable, politely suggest human support.
6. Reply in the same language as the customer.

Previous Conversation:
{history}

Knowledge Base Context:
{context}

Customer Question:
{question}

Answer:
"""

    print("3. Sending question to Gemini...")

    response = llm.invoke(prompt)

    answer = getattr(response, "content", response)

    if isinstance(answer, list):
        answer = " ".join(
            item["text"]
            for item in answer
            if isinstance(item, dict) and item.get("type") == "text"
        )

    print("4. Final Answer:", answer)

    return answer or "Gemini returned an empty response."
