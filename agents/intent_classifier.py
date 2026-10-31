def classify_intent(question):

    question = question.lower()

    intents = {
        "human_support": [
            "human", "agent", "representative",
            "talk to someone", "speak to someone",
            "complaint"
        ],
        "order_tracking": [
            "track order", "order status",
            "where is my order", "tracking"
        ],
        "refund": [
            "refund", "money back", "return my money"
        ],
        "cancellation": [
            "cancel order", "cancellation"
        ],
        "delivery": [
            "delivery", "shipping", "late delivery"
        ],
        "payment": [
            "payment", "upi", "transaction","money deducted","payment issue", "payment failed"
        ]
    }

    for intent, keywords in intents.items():
        if any(keyword in question for keyword in keywords):
            return intent

    return "general_query"