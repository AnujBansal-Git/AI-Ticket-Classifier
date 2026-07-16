from transformers import pipeline

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

_summarizer = None


def get_summarizer():
    """
    Lazily load the summarization model.
    """

    global _summarizer

    if _summarizer is None:
        _summarizer = pipeline(
            "summarization",
            model=MODEL_NAME,
        )

    return _summarizer


def generate_summary(text: str) -> str:
    """
    Generate a concise summary of a customer support ticket.
    """

    text = text.strip()

    if len(text.split()) < 15:
        return text

    greetings = [
        "Dear Support Team,",
        "Dear Support,",
        "Hello,",
        "Hi,",
    ]

    for greeting in greetings:
        if text.startswith(greeting):
            text = text[len(greeting):].strip()

    endings = [
        "Thank you.",
        "Thanks.",
        "Regards.",
        "Best regards.",
        "Sincerely.",
    ]

    for ending in endings:
        if text.endswith(ending):
            text = text[:-len(ending)].strip()

    prompt = (
        "Summarize this customer support ticket in one concise sentence:\n\n"
        + text
    )

    input_words = len(prompt.split())

    summarizer = get_summarizer()

    result = summarizer(
        prompt,
        max_length=min(60, input_words),
        min_length=10,
        do_sample=False,
    )

    summary = result[0]["summary_text"].strip()

    prefixes = [
        "Customer support ticket:",
        "Customer support ticket",
    ]

    for prefix in prefixes:
        if summary.lower().startswith(prefix.lower()):
            summary = summary[len(prefix):].strip()

    return summary.strip('"').strip()