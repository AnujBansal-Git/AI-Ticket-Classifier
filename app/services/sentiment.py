from transformers import pipeline

from transformers import pipeline

MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
)


def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of a ticket.
    """

    result = sentiment_pipeline(text)[0]

    return result["label"]