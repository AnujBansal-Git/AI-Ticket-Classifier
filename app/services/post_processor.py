def post_process(ticket, category, priority, team):
    """
    Apply business rules after ML predictions.
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
        "awesome",
        "perfect",
    ]

    # -----------------------------
    # Billing & Payments
    # -----------------------------
    billing_keywords = [
        "refund",
        "receipt",
        "invoice",
        "bill",
        "billing",
        "payment",
        "charged",
        "charge",
        "double charged",
        "subscription",
        "renewal",
        "upi",
        "credit card",
        "debit card",
        "transaction",
        "gst",
        "tax invoice",
    ]

    # -----------------------------
    # Account / Authentication
    # -----------------------------
    account_keywords = [
        "login",
        "log in",
        "password",
        "forgot password",
        "reset password",
        "account",
        "sign in",
        "signin",
        "authentication",
        "otp",
        "mfa",
        "locked",
        "unlock",
    ]

    # -----------------------------
    # Returns & Exchanges
    # -----------------------------
    return_keywords = [
        "return",
        "replace",
        "replacement",
        "exchange",
        "wrong item",
        "damaged",
        "broken product",
        "defective",
    ]

    # -----------------------------
    # Outages / Infrastructure
    # -----------------------------
    outage_keywords = [
        "server down",
        "service unavailable",
        "outage",
        "downtime",
        "network",
        "internet",
        "wifi",
        "latency",
        "dns",
    ]

    # -----------------------------
    # Technical Support
    # -----------------------------
    technical_keywords = [
        "api",
        "fastapi",
        "python",
        "exception",
        "error",
        "bug",
        "crash",
        "stack trace",
        "compile",
        "docker",
    ]

    # ==========================================================
    # Apply rules
    # ==========================================================

    if any(keyword in text for keyword in feedback_keywords):
        return (
            "Feedback",
            "low",
            "Customer Service",
        )

    if any(keyword in text for keyword in billing_keywords):
        team = "Billing and Payments"

    if any(keyword in text for keyword in account_keywords):
        team = "IT Support"

    if any(keyword in text for keyword in return_keywords):
        team = "Returns and Exchanges"

    if any(keyword in text for keyword in outage_keywords):
        team = "Service Outages and Maintenance"
        priority = "high"

    if any(keyword in text for keyword in technical_keywords):
        team = "Technical Support"

    urgency_keywords = [
        "urgent",
        "immediately",
        "asap",
        "critical",
        "production",
        "cannot",
        "can't",
        "unable",
    ]

    if any(keyword in text for keyword in urgency_keywords):
        priority = "high"

    return category, priority, team