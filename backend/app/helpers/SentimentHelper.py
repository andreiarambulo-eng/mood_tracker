"""Sentiment analysis helper using TextBlob."""
from textblob import TextBlob


class SentimentHelper:
    """Analyzes sentiment from mood remarks."""

    @staticmethod
    def analyze(text: str) -> dict:
        """
        Analyze sentiment of a text string.

        Returns:
            dict with sentiment_score (-1.0 to 1.0) and sentiment_label
        """
        if not text or not text.strip():
            return {"sentiment_score": 0.0, "sentiment_label": "Neutral"}

        blob = TextBlob(text)
        score = round(blob.sentiment.polarity, 4)

        if score > 0.1:
            label = "Positive"
        elif score < -0.1:
            label = "Negative"
        else:
            label = "Neutral"

        return {"sentiment_score": score, "sentiment_label": label}
