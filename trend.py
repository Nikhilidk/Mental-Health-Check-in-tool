import pandas as pd
import numpy as np
from sentiment import negative_word_ratio

def get_entries_dataframe(rows):
    """Convert raw SQLite rows into a pandas DataFrame."""
    df = pd.DataFrame(rows, columns=[
        "id", "date", "text", "neg", "neu", "pos", "compound", "entry_length"
    ])
    df["date"] = pd.to_datetime(df["date"])
    df["neg_ratio"] = df["text"].apply(negative_word_ratio)  
    df = df.sort_values(["date", "id"])
    return df

def daily_average(df):
    """Collapse multiple entries on the same date into one daily mean."""
    daily = (
        df.groupby(df["date"].dt.date)
          .agg(compound=("compound", "mean"),
               neg=("neg", "mean"),
               neg_ratio=("neg_ratio", "mean"),               
               entry_count=("id", "count"),
               total_words=("entry_length", "sum"))
          .reset_index()
    )
    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values("date")

def compute_trend(df, window=7):
    """Add rolling average/volatility columns; return the slope and overall volatility."""
    if df.empty:
        return df, None, None

    df = df.copy()
    df["rolling_avg"] = df["compound"].rolling(window=window, min_periods=1).mean()
    df["rolling_std"] = df["compound"].rolling(window=window, min_periods=2).std()

    df["day_index"] = (df["date"] - df["date"].min()).dt.days

    slope = None
    if len(df) >= 2 and df["day_index"].nunique() >= 2:
        slope = np.polyfit(df["day_index"], df["compound"], 1)[0]

    volatility = df["compound"].std() if len(df) >= 2 else None

    return df, slope, volatility

def get_trend_summary(df, slope, volatility,
                      slope_threshold=0.02, volatility_threshold=0.35):
    """Combine slope + volatility into a gentle, plain-language summary."""
    if slope is None or volatility is None:
        return "Not enough entries yet to detect a trend."

    overall_mean = df["compound"].mean()
    recent_mean = df["compound"].tail(2).mean()  # now = last two days

    if volatility > volatility_threshold:
        if recent_mean > overall_mean + 0.2:
            return "Your mood has swung quite a bit lately, but your most recent entries are on a brighter note."
        elif recent_mean < overall_mean - 0.2:
            return "Your mood has swung quite a bit lately, and your most recent entries are lower. Be kind to yourself, and consider talking to someone you trust."
        else:
            return "Your mood has been up and down lately."

    if slope > slope_threshold:
        return "Your mood has been trending more positive recently."
    elif slope < -slope_threshold:
        return "Your mood has been trending lower recently. It might be worth checking in with yourself, or talking to someone you trust."
    else:
        return "Your mood has been relatively steady recently."