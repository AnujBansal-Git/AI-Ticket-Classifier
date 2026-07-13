from pathlib import Path

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"

MODELS_DIR.mkdir(exist_ok=True)


def save_model(model, vectorizer, model_name: str):
    """
    Save a trained model and its vectorizer.
    """

    model_path = MODELS_DIR / f"{model_name}_model.pkl"
    vectorizer_path = MODELS_DIR / f"{model_name}_vectorizer.pkl"

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print(f"Model saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")

def load_model(model_name: str):
    """
    Load a trained model and its vectorizer.
    """

    model_path = MODELS_DIR / f"{model_name}_model.pkl"
    vectorizer_path = MODELS_DIR / f"{model_name}_vectorizer.pkl"

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    return model, vectorizer