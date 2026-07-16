from app.ml.trainer import train_model


TARGETS = [
    "category",
    "priority",
    "team",
]

for target in TARGETS:

    result = train_model(target)

    print("\n" + "=" * 80)
    print(f"{target.upper()} - WRONG PREDICTIONS")
    print("=" * 80)

    X_test = result["X_test"].reset_index(drop=True)
    y_test = result["y_test"].reset_index(drop=True)
    predictions = result["predictions"]

    mistakes = 0

    for i in range(len(predictions)):

        if predictions[i] != y_test.iloc[i]:

            mistakes += 1

            print(f"\nMistake #{mistakes}")

            print("-" * 80)

            print("Ticket:")
            print(X_test.iloc[i])

            print()

            print("Actual:")
            print(y_test.iloc[i])

            print()

            print("Predicted:")
            print(predictions[i])

            print("-" * 80)

        if mistakes == 30:
            break