from pathlib import Path

import pandas as pd

from app.ml.preprocessing import clean_text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = (
    PROJECT_ROOT
    / "sample_data"
    / "aa_dataset-tickets-multi-lang-5-2-50-version.csv"
)


def load_training_data():
    """
    Load and prepare the ticket dataset.
    """

    df = pd.read_csv(DATASET_PATH)

    # Keep only English tickets
    df = df[df["language"] == "en"].copy()

    # Fill missing subjects
    df["subject"] = df["subject"].fillna("")

    # Combine subject and body
    df["ticket"] = df["subject"] + " " + df["body"]

    # Keep only required columns
    df = df[
        [
            "ticket",
            "type",
            "priority",
            "queue",
        ]
    ]

    # Rename columns to match our project
    df = df.rename(
        columns={
            "type": "category",
            "queue": "team",
        }
    )

    # Clean ticket text
    df["ticket"] = df["ticket"].apply(clean_text)

    return df