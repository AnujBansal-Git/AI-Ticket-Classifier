import sys

from app.ml.trainer import train_model


def main():
    if len(sys.argv) > 1:
        target_column = sys.argv[1]
    else:
        target_column = "category"

    result = train_model(target_column)

    print("=" * 60)
    print(f"{target_column.upper()} MODEL")
    print("=" * 60)

    print(f"Accuracy : {result['accuracy']:.4f}")

    print()

    print("=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)

    print(result["report"])

    print()

    print("=" * 60)
    print("SAMPLE PREDICTIONS")
    print("=" * 60)

    X_test = result["X_test"]
    y_test = result["y_test"]
    predictions = result["predictions"]

    for i in range(5):
        print(f"\nTicket:")
        print(X_test.iloc[i])

        print("\nActual:")
        print(y_test.iloc[i])

        print("\nPredicted:")
        print(predictions[i])

        print("-" * 60)


if __name__ == "__main__":
    main()