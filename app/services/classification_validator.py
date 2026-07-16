import re


BUSINESS_KEYWORDS = {
    "refund",
    "payment",
    "invoice",
    "receipt",
    "billing",
    "charged",
    "password",
    "login",
    "account",
    "locked",
    "otp",
    "server",
    "network",
    "internet",
    "outage",
    "error",
    "bug",
    "crash",
    "api",
    "subscription",
    "return",
    "replace",
    "exchange",
    "delivery",
    "order",
    "cancel",
}


def is_classifiable(ticket: str) -> bool:
    """
    Returns True if the ticket contains enough meaningful
    information to attempt classification.
    """

    ticket = ticket.strip().lower()

    if not ticket:
        return False

    words = re.findall(r"[a-z]+", ticket)

    if not words:
        return False

    # Strong business keywords should always be accepted.
    if any(word in BUSINESS_KEYWORDS for word in words):
        return True

    # Otherwise apply generic validation.

    if len(ticket) < 10:
        return False

    if len(words) < 3:
        return False

    if len(set(words)) < 2:
        return False

    alphabetic_ratio = (
        sum(c.isalpha() for c in ticket)
        / len(ticket)
    )

    if alphabetic_ratio < 0.5:
        return False

    return True