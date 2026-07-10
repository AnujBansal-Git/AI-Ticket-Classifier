from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = (
    PROJECT_ROOT
    / "sample_data"
    / "aa_dataset-tickets-multi-lang-5-2-50-version.csv"
)


def main():
    df = pd.read_csv(DATASET_PATH)

    print("=" * 60)
    print("DATASET SHAPE")
    print("=" * 60)
    print(df.shape)

    print("\n" + "=" * 60)
    print("LANGUAGES")
    print("=" * 60)
    print(df["language"].value_counts())

    print("\n" + "=" * 60)
    print("TICKET TYPES")
    print("=" * 60)
    print(df["type"].value_counts())

    print("\n" + "=" * 60)
    print("QUEUES")
    print("=" * 60)
    print(df["queue"].value_counts())

    print("\n" + "=" * 60)
    print("PRIORITIES")
    print("=" * 60)
    print(df["priority"].value_counts())


if __name__ == "__main__":
    main()