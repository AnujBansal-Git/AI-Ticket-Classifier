from app.services.summary import generate_summary

tickets = [
    """
    Dear Support Team,

    My laptop has been disconnecting from the WiFi every few minutes for the last two days.
    I restarted the laptop, updated the drivers, reset the router and even tested with another network.
    The issue still persists.
    I need this fixed urgently because I cannot work remotely.

    Thank you.
    """,

    """
    Hello,

    I was charged twice for the same subscription.
    My bank statement clearly shows two transactions.
    Please refund the duplicate payment as soon as possible.

    Regards.
    """,

    """
    Hi,

    I cannot log into my account anymore.
    I already reset my password twice.
    Every login attempt says my credentials are invalid.

    Thanks.
    """
]

for i, ticket in enumerate(tickets, start=1):
    print("=" * 80)
    print(f"TICKET {i}")
    print("=" * 80)

    print("\nORIGINAL\n")
    print(ticket.strip())

    print("\nSUMMARY\n")
    print(generate_summary(ticket))

    print("\n")