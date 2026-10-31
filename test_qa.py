from rag.qa_chain import ask_question

question = "What are the customer support working hours?"

print("Customer Question:", question)
print("\nAI Answer:")
print(ask_question(question))