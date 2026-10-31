
from typing import TypedDict, List, Dict, Optional

from langgraph.graph import StateGraph, START, END

from rag.qa_chain import ask_question
from database.ticket_db import create_ticket
from agents.intent_classifier import classify_intent


# ---------------- STATE ----------------

class SupportState(TypedDict):
    question: str
    category: str
    answer: str
    ticket_id: str
    chat_history: List[Dict[str, str]]
    customer_name: str
    customer_email: str
    user_id: Optional[int]


# ---------------- STEP 1: CLASSIFY INTENT ----------------

def classify_query(state: SupportState):

    category = classify_intent(state["question"])

    print("Detected Intent:", category)

    return {"category": category}


# ---------------- STEP 2: GENERATE RAG ANSWER ----------------

def answer_question(state: SupportState):

    answer = ask_question(
        question=state["question"],
        chat_history=state.get("chat_history", []),
        intent=state["category"]
    )

    return {"answer": answer}


# ---------------- STEP 3: CREATE SUPPORT TICKET ----------------

def create_support_ticket(state: SupportState):

    try:
        ticket_id = create_ticket(
            issue=state["question"],
            customer_name=state.get("customer_name", "Guest"),
            customer_email=state.get("customer_email", ""),
            user_id=state.get("user_id")
        )

        answer = (
            "Your request has been escalated to human support. "
            "Your support ticket has been created successfully. "
            f"Your Ticket ID is: {ticket_id}. "
            "Our support team will follow up with you."
        )

        return {
            "ticket_id": ticket_id,
            "answer": answer
        }

    except PermissionError:
        return {
            "ticket_id": "",
            "answer": (
                "Please login with a valid customer account "
                "to create a support ticket."
            )
        }

    except Exception as e:
        print("Ticket creation error:", e)

        return {
            "ticket_id": "",
            "answer": (
                "Sorry, we could not create your support ticket. "
                "Please try again."
            )
        }


# ---------------- STEP 4: ROUTING ----------------

def route_query(state: SupportState):

    if state["category"] == "human_support":
        return "ticket"

    return "faq"


# ---------------- STEP 5: BUILD LANGGRAPH ----------------

workflow = StateGraph(SupportState)

workflow.add_node("classify", classify_query)
workflow.add_node("faq", answer_question)
workflow.add_node("ticket", create_support_ticket)

workflow.add_edge(START, "classify")

workflow.add_conditional_edges(
    "classify",
    route_query,
    {
        "faq": "faq",
        "ticket": "ticket"
    }
)

workflow.add_edge("faq", END)
workflow.add_edge("ticket", END)

support_agent = workflow.compile()


# ---------------- STEP 6: RUN AGENT ----------------

def run_support_agent(
    question,
    chat_history=None,
    customer_name="Guest",
    customer_email="",
    user_id=None
):

    result = support_agent.invoke({

        "question": question,
        "category": "",
        "answer": "",
        "ticket_id": "",
        "chat_history": chat_history or [],

        "customer_name": customer_name,
        "customer_email": customer_email,
        "user_id": user_id

    })

    return result
