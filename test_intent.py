from agents.intent_classifier import classify_intent

questions = [
    "Where is my order?",
    "I want my refund",
    "Please cancel my order",
    "My payment failed",
    "I want to talk to a human",
    "Hello, how are you?"
]

for question in questions:
    result = classify_intent(question)
    print(question, "---->", result)