from app.ml.data_loader import load_training_data


def main():
    df = load_training_data()

    print("=" * 60)
    print(df.head())

    print()

    print(df.info())

    print()

    print(df["category"].value_counts())

    print()

    print(df["priority"].value_counts())

    print()

    print(df["team"].value_counts())


if __name__ == "__main__":
    main()