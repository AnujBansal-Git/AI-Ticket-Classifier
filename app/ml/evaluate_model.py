from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from app.ml.trainer import train_model


TARGETS = [
    "category",
    "priority",
    "team",
]


for target in TARGETS:

    result = train_model(target)

    print("\n" + "=" * 70)
    print(target.upper())
    print("=" * 70)

    print(f"Accuracy: {result['accuracy']:.4f}")

    print("\nClassification Report:\n")

    print(result["report"])

    print("\nConfusion Matrix:\n")

    print(
        confusion_matrix(
            result["y_test"],
            result["predictions"],
        )
    )