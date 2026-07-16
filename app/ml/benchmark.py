import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from app.ml.data_loader import load_training_data


def evaluate_model(name, model, X_train, X_test, y_train, y_test):
    start = time.time()

    model.fit(X_train, y_train)

    train_time = time.time() - start

    start = time.time()

    predictions = model.predict(X_test)

    prediction_time = time.time() - start

    accuracy = accuracy_score(y_test, predictions)

    print("=" * 60)
    print(name)
    print("=" * 60)
    print(f"Accuracy       : {accuracy:.4f}")
    print(f"Training Time  : {train_time:.3f} sec")
    print(f"Prediction Time: {prediction_time:.3f} sec")
    print()


def main():
    df = load_training_data()

    X = df["ticket"]
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

    vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
)   


    X_train = vectorizer.fit_transform(X_train)
    X_test = vectorizer.transform(X_test)

    evaluate_model(
        "Multinomial Naive Bayes",
        MultinomialNB(),
        X_train,
        X_test,
        y_train,
        y_test,
    )

    evaluate_model(
        "Logistic Regression",
        LogisticRegression(max_iter=1000),
        X_train,
        X_test,
        y_train,
        y_test,
    )

    evaluate_model(
        "Linear SVM",
        LinearSVC(),
        X_train,
        X_test,
        y_train,
        y_test,
    )


if __name__ == "__main__":
    main()