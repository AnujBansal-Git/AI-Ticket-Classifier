def post_process(ticket, category, priority, team):
    """
    Apply simple business rules after ML predictions.
    """

    text = ticket.lower()

    # -----------------------------
    # Positive feedback
    # -----------------------------
    feedback_keywords = [
        "thank you",
        "thanks",
        "great support",
        "resolved",
        "appreciate",
        "excellent service",
        "good job",
    ]

    if any(keyword in text for keyword in feedback_keywords):
        category = "Feedback"
        priority = "low"
        team = "Customer Service"

    # -----------------------------
    # Billing
    # -----------------------------
    billing_keywords = [
        "refund",
        "charged",
        "invoice",
        "payment",
        "subscription",
        "billing",
    ]

    if any(keyword in text for keyword in billing_keywords):
        team = "Billing and Payments"

    # -----------------------------
    # Account
    # -----------------------------
    account_keywords = [
        "password",
        "login",
        "account",
        "sign in",
        "locked",
    ]

    if any(keyword in text for keyword in account_keywords):
        team = "IT Support"

    return category, priority, team