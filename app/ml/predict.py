from app.ml.model_io import load_model
from app.ml.preprocessing import clean_text


def predict(ticket: str, model_name: str) -> str:
    """
    Predict using any trained model.
    """

    model, vectorizer = load_model(model_name)

    cleaned_ticket = clean_text(ticket)

    ticket_vector = vectorizer.transform([cleaned_ticket])

    prediction = model.predict(ticket_vector)

    return prediction[0]