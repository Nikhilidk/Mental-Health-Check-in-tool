import sqlite3, pandas as pd
from sentiment import analyze_text
from nltk.sentiment import SentimentIntensityAnalyzer

conn = sqlite3.connect("data/entries.db")
df = pd.read_sql_query(
    "SELECT date, text, mood_rating FROM entries WHERE mood_rating IS NOT NULL", conn)
conn.close()
print("Rated entries:", len(df))

stock = SentimentIntensityAnalyzer()   # unmodified VADER, for comparison
df["stock"] = df["text"].apply(lambda t: stock.polarity_scores(t)["compound"])
df["custom"] = df["text"].apply(lambda t: analyze_text(t)[3])   # with your custom lexicon

lab = lambda c: "pos" if c >= 0.05 else "neg" if c <= -0.05 else "neu"
true = df["mood_rating"].apply(lambda r: "neg" if r <= 2 else "neu" if r == 3 else "pos")

for col in ["stock", "custom"]:
    print(col,
          "| pearson", round(df[col].corr(df["mood_rating"]), 3),
          "| spearman", round(df[col].rank().corr(df["mood_rating"].rank()), 3),
          "| accuracy", round((df[col].apply(lab) == true).mean(), 3))

print()
print(pd.crosstab(true, df["custom"].apply(lab), rownames=["self"], colnames=["vader"]))

df["miss"] = (3 + 2 * df["custom"] - df["mood_rating"]).abs()
print()
print(df[true != df["custom"].apply(lab)]
      .sort_values("miss", ascending=False)[["date", "mood_rating", "custom", "text"]]
      .head(6).to_string())