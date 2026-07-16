import pandas as pd

from app.services.bulk_classifier import classify_dataframe


df = pd.DataFrame(
    {
        "ticket": [
            "My laptop crashes every few minutes.",
            "I was charged twice for my subscription.",
            "Thank you for resolving my issue.",
        ]
    }
)

result = classify_dataframe(df)

print(result)