from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of a ticket.
    """

    score = analyzer.polarity_scores(text)["compound"]

    if score >= 0.05:
        return "POSITIVE"

    if score <= -0.05:
        return "NEGATIVE"

    return "NEUTRAL"