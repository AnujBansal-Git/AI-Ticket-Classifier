from app.services.sentiment import analyze_sentiment


tickets = [
    "My laptop keeps crashing and nothing works anymore.",
    "Please help me reset my password.",
    "Thank you very much for resolving my issue quickly!",
]

for ticket in tickets:
    print("=" * 60)
    print(ticket)
    print()
    print("Sentiment:", analyze_sentiment(ticket))