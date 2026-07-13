from app.services.summary import generate_summary


def main():
    ticket = """
    Dear Support Team,

    My laptop has been disconnecting from the WiFi every few minutes for the last two days.
    I restarted the laptop, updated the drivers, reset the router and even tested with another network.
    The issue still persists.
    I need this fixed urgently because I cannot work remotely.

    Thank you.
    """

    print("=" * 60)
    print("ORIGINAL")
    print("=" * 60)
    print(ticket)

    print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(generate_summary(ticket))


if __name__ == "__main__":
    main()