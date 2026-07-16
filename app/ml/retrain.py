import pandas as pd

from app.ml.data_loader import (
    load_feedback_data,
    load_training_data,
)
from app.ml.trainer import train_model


def main():
    """
    Retrain all models using the original dataset
    plus manually reviewed tickets.
    """

    original_df = load_training_data()
    feedback_df = load_feedback_data()

    combined_df = pd.concat(
        [original_df, feedback_df],
        ignore_index=True,
    )

    print(f"Original samples : {len(original_df)}")
    print(f"Feedback samples : {len(feedback_df)}")
    print(f"Total samples    : {len(combined_df)}")

    print("\nRetraining category model...")
    train_model("category", combined_df)

    print("\nRetraining priority model...")
    train_model("priority", combined_df)

    print("\nRetraining team model...")
    train_model("team", combined_df)

    print("\nRetraining complete.")


if __name__ == "__main__":
    main()