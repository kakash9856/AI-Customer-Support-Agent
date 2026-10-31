
import traceback

from rag.vector_store import get_vector_store
from config import llm


def extract_answer(response):
    """Extract readable text from Gemini's response."""

    content = getattr(response, "content", response)

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

        return "\n".join(
            part for part in text_parts if part
        ).strip()

    return ""


def ask_question(question, chat_history=None, intent="general_query"):

    print("1. Searching Knowledge Base...")
    print("Detected Intent:", intent)

    try:
        vector_store = get_vector_store()

        docs = vector_store.similarity_search(
            question,
            k=4
        )

        print("2. Retrieved documents:", len(docs))

        for i, doc in enumerate(docs):
            print(f"Document {i + 1}:")
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
1. Answer using only the knowledge base context.
2. Never invent company policies.
3. Reply in the same language as the customer.
4. Give a clear and direct answer.
5. If information is unavailable, suggest human support.

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

        print("Gemini response type:", type(response))
        print("Gemini raw response:", repr(response))
        print("Gemini metadata:", getattr(response, "response_metadata", {}))

        answer = extract_answer(response)

        print("4. Final Answer:", repr(answer))

        if not answer:
            return (
                "I received an empty response from the AI service. "
                "Please try again."
            )

        return answer

    except Exception as e:
        print("RAG ERROR:", repr(e))
        traceback.print_exc()

        return (
            "Sorry, the AI service encountered an error. "
            "Please try again."
        )
