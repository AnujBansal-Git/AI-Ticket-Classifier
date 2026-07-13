from app.ml.predict import predict


def main():
    ticket = """
    My laptop keeps disconnecting from the WiFi every few minutes.
    """

    print("Ticket:")
    print(ticket)

    print()

    print("Category:")
    print(predict(ticket, "category"))

    print()

    print("Priority:")
    print(predict(ticket, "priority"))


if __name__ == "__main__":
    main()