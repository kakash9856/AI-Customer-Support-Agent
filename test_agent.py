from agents.support_agent import run_support_agent

# Test 1: Normal customer query
result = run_support_agent("How can I track my order?")

print("\n--- FAQ TEST ---")
print("Category:", result["category"])
print("Answer:", result["answer"])


# Test 2: Human support request
result = run_support_agent("I want to talk to a human agent")

print("\n--- HUMAN SUPPORT TEST ---")
print("Category:", result["category"])
print("Answer:", result["answer"])
print("Ticket ID:", result["ticket_id"])