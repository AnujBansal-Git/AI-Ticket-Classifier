from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "sample_data" / "customer_support_tickets.csv"


def main():
    df = pd.read_csv(DATASET_PATH)

    for _, row in df.head(30).iterrows():
        print("-" * 80)
        print("Subject :", row["Ticket Subject"])
        print("Category:", row["Ticket Type"])
        print("Description:")
        print(row["Ticket Description"])


if __name__ == "__main__":
    main()