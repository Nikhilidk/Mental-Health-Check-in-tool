import pandas as pd
import numpy as np

def get_entries_dataframe(rows):
    """Convert raw SQLite rows into a pandas DataFrame."""
    df = pd.DataFrame(rows, columns=[
        "id", "date", "text", "neg", "neu", "pos", "compound", "entry_length"
    ])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df

def compute_trend(df, window=7):
    """Add a rolling average column and compute an overall trend slope."""
    if df.empty:
        return df, None

    df = df.copy()
    df["rolling_avg"] = df["compound"].rolling(window=window, min_periods=1).mean()

    # Simple linear regression slope over time (day index as x)
    df["day_index"] = (df["date"] - df["date"].min()).dt.days
    if len(df) >= 2:
        slope = np.polyfit(df["day_index"], df["compound"], 1)[0]
    else:
        slope = None

    return df, slope

def get_trend_summary(slope):
    """Turn a numeric slope into a human-readable trend label."""
    if slope is None:
        return "Not enough entries yet to detect a trend."
    if slope > 0.02:
        return "Your mood has been trending more positive recently."
    elif slope < -0.02:
        return "Your mood has been trending lower recently — might be worth checking in with yourself, or talking to someone you trust."
    else:
        return "Your mood has been relatively stable recently."

def compute_trend(df, window=7):
    """Add a rolling average column and compute an overall trend slope."""
    if df.empty:
        return df, None

    df = df.copy()
    df["rolling_avg"] = df["compound"].rolling(window=window, min_periods=1).mean()

    df["day_index"] = (df["date"] - df["date"].min()).dt.days

    # Need at least 2 distinct days to fit a meaningful trend line
    if len(df) >= 2 and df["day_index"].nunique() >= 2:
        slope = np.polyfit(df["day_index"], df["compound"], 1)[0]
    else:
        slope = None

    return df, slope