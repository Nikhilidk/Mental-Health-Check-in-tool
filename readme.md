# Mental Wellness Journal

A voice-and-text journaling app that analyses your entries over time and shows a general picture of your mood trends. It runs entirely on your own computer: transcription, analysis and storage are all local.

> **This is a self-reflection tool, not a medical or diagnostic tool.** It looks at patterns in the words you write. It cannot tell you whether you have a mental health condition, and it does not assess risk. If you are struggling, please talk to someone you trust or a professional.

## What it does

- **Journal by voice or text.** Record an entry in the browser and it is transcribed locally with Whisper. The transcript appears in an editable box, so you can fix any mistakes before saving.
- **Rate your mood.** Pick a face (1-5) with each entry. This is your own self-reported mood, used to check how well the analysis matches how you actually felt.
- **Score every entry.** Each entry gets a sentiment score from VADER.
- **See trends over time.** Entries are averaged per day, then analysed over a selectable window (7, 14, 30 or 90 days).
- **Get a plain-language summary.** For example "Your mood has been up and down lately", or a gentle suggestion to talk to someone if your last three days have all been low.

## Indicators

| Indicator | What it measures |
|---|---|
| Average sentiment | Daily mean of VADER's compound score (-1 to +1), plus a rolling average |
| Mood variability | Standard deviation of daily scores. Large swings can point to an unsettled period |
| Trend slope | Linear-regression slope of daily scores: improving, flat or declining |
| Negative-word ratio | Share of words that VADER's lexicon rates as negative |
| Journaling activity | Entries and words written per day. A sharp drop in how much you write is flagged |
| Weekly summary | Average mood, variability and negative language per calendar week, with a comparison to the previous week |

VADER's lexicon is extended with a small set of mental-health words (such as *overwhelmed*, *drained*, *pointless*) that the stock lexicon misses.

## How it works

```
voice recording -> Whisper (small, local) -> text
text -> VADER + custom lexicon -> scores -> SQLite
SQLite -> daily averages -> trend / variability / weekly analysis -> Streamlit dashboard
```

## Tech stack

Python, [Streamlit](https://streamlit.io), [OpenAI Whisper](https://github.com/openai/whisper) (speech-to-text), [NLTK VADER](https://www.nltk.org) (sentiment), pandas / NumPy (analysis), SQLite (storage).

## Setup

Tested on Windows 11 with Python 3.12.

### 1. Prerequisites

- **Python 3.12** (or a close version)
- **FFmpeg**, which Whisper needs to read audio. It must be on your PATH:
  - Windows: `winget install ffmpeg`, then restart the terminal
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Check with `ffmpeg -version`

### 2. Install

```bash
git clone https://github.com/Nikhilidk/Mental-Health-Check-in-tool
cd Mental-Health-Check-in-tool

python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon')"
```

If PowerShell blocks the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

### 3. Run

```bash
streamlit run app.py
```

The app opens at http://localhost:8501.

**First launch:** Whisper downloads its `small` model (about 460 MB) once and caches it. Make sure you are on a stable connection, because an interrupted download causes a checksum error. If that happens, delete `%USERPROFILE%\.cache\whisper\small.pt` and try again.

## Using the app

1. Type an entry, or record one with the microphone (allow microphone access in your browser).
2. If you recorded, check the transcript and fix any errors.
3. Pick a mood face (optional) and click **Save Entry**.
4. Trend charts appear once you have entries on **at least two different days**.

On a CPU-only laptop, transcription takes roughly as long as the recording (about 13 seconds for a 10-second clip with the `small` model).

## Evaluation

To check whether the sentiment scores reflect how the user actually felt, 20 journal entries (1-20 October) were each rated 1-5 by the same person at the time of writing, then compared with VADER's score:

| | Pearson | Spearman | 3-class accuracy |
|---|---|---|---|
| Stock VADER | 0.821 | 0.854 | 0.65 |
| VADER + custom lexicon | 0.829 | 0.861 | 0.65 |

- VADER's scores track self-rated mood strongly.
- Three-class accuracy is lower because VADER almost never predicts "neutral" on multi-sentence entries. Ignoring neutral-rated entries, it picked the correct direction (positive or negative) for 13 of 15 entries.
- The custom lexicon changed results only slightly on this data.
- Most errors were entries that mention a hard moment followed by coping language (for example "still rough, but I watched a comfort movie"), where lexicon-based scoring overweights the positive words.

This is a small, single-participant evaluation, so treat the results as indicative. The entries are private journal text and are not included in this repository. `evaluate.py` reproduces the comparison on any local database that has rated entries.

## Limitations

- Lexicon-based sentiment cannot read context, hedging or mixed feelings well.
- It does not detect crisis, self-harm risk or any clinical condition, and it is not designed to.
- Transcription can mishear words, which is why the transcript is editable before saving.
- English only.
- The evaluation used one participant and 20 entries.

## Privacy

Everything runs locally. Audio is transcribed on your machine, and entries are stored in a local SQLite file (`data/entries.db`), which is excluded from version control. Nothing is sent to any server or API.

## Project structure

```
app.py          Streamlit UI and dashboard
transcribe.py   Whisper speech-to-text
sentiment.py    VADER scoring, custom lexicon, negative-word ratio
trend.py        Daily aggregation, trend, variability, weekly summary, nudge
database.py     SQLite storage
evaluate.py     Compares VADER scores with self-rated mood
data/           Local database (not committed)
sample_data/    Placeholder for example data
```

## Future work

- Compare VADER against transformer-based emotion models
- Better handling of mixed and hedged sentiment
- Evaluate with more participants

## Author

Nikhil Negi
Built as a beginner project with ML+NLP integration