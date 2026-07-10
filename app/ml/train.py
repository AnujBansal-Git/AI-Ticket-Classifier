from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from app.ml.preprocessing import clean_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "sample_data" / "customer_support_tickets.csv"


def load_training_data():
    """
    Load and prepare the dataset for training.
    """

    df = pd.read_csv(DATASET_PATH)

    # Keep only required columns
    df = df[
        [
            "Ticket Description",
            "Ticket Type",
            "Ticket Priority",
        ]
    ]

    # Rename columns
    df = df.rename(
        columns={
            "Ticket Description": "ticket",
            "Ticket Type": "category",
            "Ticket Priority": "priority",
        }
    )

    # Clean ticket text
    df["ticket"] = df["ticket"].apply(clean_text)

    return df


def main():
    # Load dataset
    df = load_training_data()

    # Features and labels
    X = df["ticket"]
    y = df["category"]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    # Convert text into TF-IDF vectors
    vectorizer = TfidfVectorizer()

    X_train_vectors = vectorizer.fit_transform(X_train)
    X_test_vectors = vectorizer.transform(X_test)

    print("=" * 50)
    print("TRAIN / TEST SPLIT")
    print("=" * 50)

    print(f"Training samples : {len(X_train)}")
    print(f"Testing samples  : {len(X_test)}")

    print()

    print("Training matrix shape:")
    print(X_train_vectors.shape)

    print()

    print("Testing matrix shape:")
    print(X_test_vectors.shape)

    print()

    print("Vocabulary size:")
    print(len(vectorizer.vocabulary_))


if __name__ == "__main__":
    main()