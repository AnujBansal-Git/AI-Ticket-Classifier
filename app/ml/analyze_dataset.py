from pathlib import Path

import pandas as pd


# Project root -> sample_data -> customer_support_tickets.csv
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "sample_data" / "customer_support_tickets.csv"


def main():
    df = pd.read_csv(DATASET_PATH)

    print("=" * 50)
    print("DATASET SHAPE")
    print("=" * 50)
    print(df.shape)

    print("\n" + "=" * 50)
    print("COLUMNS")
    print("=" * 50)
    print(df.columns.tolist())

    print("\n" + "=" * 50)
    print("MISSING VALUES")
    print("=" * 50)
    print(df.isnull().sum())

    print("\n" + "=" * 50)
    print("TICKET TYPE DISTRIBUTION")
    print("=" * 50)
    print(df["Ticket Type"].value_counts())

    print("\n" + "=" * 50)
    print("PRIORITY DISTRIBUTION")
    print("=" * 50)
    print(df["Ticket Priority"].value_counts())

    print("\n" + "=" * 50)
    print("DUPLICATE ROWS")
    print("=" * 50)
    print(df.duplicated().sum())


if __name__ == "__main__":
    main()