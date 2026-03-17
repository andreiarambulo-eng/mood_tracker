"""Sentiment analysis helper using TextBlob."""
import os
import nltk

# Ensure NLTK data is available (for serverless environments like Vercel)
_nltk_data_path = os.path.join('/tmp', 'nltk_data')
if not os.path.exists(os.path.join(_nltk_data_path, 'tokenizers')):
    os.makedirs(_nltk_data_path, exist_ok=True)
    nltk.data.path.insert(0, _nltk_data_path)
    try:
        nltk.download('punkt_tab', download_dir=_nltk_data_path, quiet=True)
        nltk.download('averaged_perceptron_tagger_eng', download_dir=_nltk_data_path, quiet=True)
    except Exception:
        pass

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
