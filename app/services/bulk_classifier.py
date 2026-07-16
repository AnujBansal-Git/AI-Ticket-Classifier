import pandas as pd

from app.ml.predict import predict
from app.services.post_processor import post_process
from app.services.sentiment import analyze_sentiment
from app.services.summary import generate_summary


def classify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify every ticket in a dataframe.
    Expects a column named 'ticket'.
    """

    results = []

    for ticket in df["ticket"]:

        category = predict(ticket, "category")
        priority = predict(ticket, "priority")
        team = predict(ticket, "team")

        category, priority, team = post_process(
            ticket,
            category,
            priority,
            team,
        )

        summary = generate_summary(ticket)
        sentiment = analyze_sentiment(ticket)

        results.append(
            {
                "ticket": ticket,
                "category": category,
                "priority": priority,
                "suggested_team": team,
                "summary": summary,
                "sentiment": sentiment,
            }
        )

    return pd.DataFrame(results)