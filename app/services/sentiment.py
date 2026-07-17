from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

NEGATIVE_ISSUE_TERMS = [
    "unable",
    "cannot",
    "can't",
    "error",
    "failed",
    "failure",
    "invalid",
    "not working",
    "bug",
    "issue",
    "problem",
    "down",
    "unavailable",
    "broken",
]


def analyze_sentiment(text: str) -> str:
    text_lower = text.lower()

    if any(term in text_lower for term in NEGATIVE_ISSUE_TERMS):
        return "NEGATIVE"

    score = analyzer.polarity_scores(text)["compound"]

    if score >= 0.05:
        return "POSITIVE"
    elif score <= -0.05:
        return "NEGATIVE"
    else:
        return "NEUTRAL"