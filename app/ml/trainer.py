from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from app.ml.data_loader import load_training_data
from app.ml.model_io import save_model

def train_model(target_column: str):
    """
    Train a Naive Bayes model for the given target column.
    """

    df = load_training_data()

    X = df["ticket"]
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    vectorizer = TfidfVectorizer()

    X_train_vectors = vectorizer.fit_transform(X_train)
    X_test_vectors = vectorizer.transform(X_test)

    model = LinearSVC()

    model.fit(X_train_vectors, y_train)

    predictions = model.predict(X_test_vectors)

    accuracy = accuracy_score(y_test, predictions)
    
    report = classification_report(
    y_test,
    predictions,
    )

    save_model(
    model=model,
    vectorizer=vectorizer,
    model_name=target_column,
    )

    return {
        "model": model,
        "vectorizer": vectorizer,
        "accuracy": accuracy,
        "predictions": predictions,
        "report": report,
        "X_test": X_test,
        "y_test": y_test,
    }