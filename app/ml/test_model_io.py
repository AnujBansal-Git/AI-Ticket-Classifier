from app.ml.model_io import load_model


def main():
    model, vectorizer = load_model("category")

    print("Model loaded successfully!")
    print(type(model))

    print()

    print("Vectorizer loaded successfully!")
    print(type(vectorizer))


if __name__ == "__main__":
    main()