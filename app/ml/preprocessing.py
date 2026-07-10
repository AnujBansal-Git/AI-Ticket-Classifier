import re


COMMON_PHRASES = [
    "im having an issue with the",
    "im facing a problem with my",
    "please assist",
    "if you require any further information",
    "thank you",
]


def clean_text(text: str) -> str:
    text = text.lower()

    # Remove placeholders
    text = re.sub(r"\{.*?\}", " ", text)

    # Remove common template phrases
    for phrase in COMMON_PHRASES:
        text = text.replace(phrase, " ")

    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()