import re
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

CUSTOM_WORDS = {
    "overwhelmed": -2.0,
    "rough": -1.5,
    "drained": -1.8,
    "pointless": -2.2,
    "burnt": -1.8,
    "hopeless": -2.5,
}
sia.lexicon.update(CUSTOM_WORDS)

def analyze_text(text):
    scores = sia.polarity_scores(text)
    entry_length = len(text.split())
    return scores["neg"], scores["neu"], scores["pos"], scores["compound"], entry_length

def negative_word_ratio(text):
    """Fraction of words that VADER's lexicon rates as negative."""
    words = re.findall(r"[a-zA-Z']+", text.lower())
    if not words:
        return 0.0
    negative = sum(1 for w in words if sia.lexicon.get(w, 0) < 0)
    return negative / len(words)