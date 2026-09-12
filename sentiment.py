from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

def analyze_text(text):
    scores = sia.polarity_scores(text)
    entry_length = len(text.split())
    return scores["neg"], scores["neu"], scores["pos"], scores["compound"], entry_length