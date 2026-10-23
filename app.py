import streamlit as st
from datetime import date
from database import init_db, add_entry, get_all_entries, delete_entry
from sentiment import analyze_text
from transcribe import transcribe_audio
from trend import (get_entries_dataframe, daily_average, compute_trend,
                   get_trend_summary, filter_window, weekly_summary,
                   get_support_nudge)

st.set_page_config(page_title="Mental Wellness Journal", layout="wide")

init_db()

st.title("Mental Wellness Journal")
st.info(
    "This journal is a self-reflection tool, not a medical or diagnostic tool. "
    "It looks at patterns in the words you write and cannot tell you whether you "
    "have a mental health condition. If you're struggling, please consider talking "
    "to someone you trust or a professional."
)

if "form_n" not in st.session_state:
    st.session_state["form_n"] = 0
n = st.session_state["form_n"]   # bumped after each save to reset the form

left, right = st.columns([1, 2], gap="large")

# ---------------- LEFT: new entry ----------------
with left:
    st.subheader("New entry")
    entry_text = st.text_area("Type how you're feeling", height=120, key=f"entry_text_{n}")
    audio_value = st.audio_input("Or record a voice entry", key=f"audio_{n}")

    final_text = None

    if audio_value is not None:
        # Transcribe only when the recording actually changes, not on every rerun
        audio_bytes = audio_value.getvalue()
        if st.session_state.get(f"last_audio_{n}") != audio_bytes:
            st.session_state[f"last_audio_{n}"] = audio_bytes
            with st.spinner("Transcribing..."):
                st.session_state[f"transcript_{n}"] = transcribe_audio(audio_value)
        final_text = st.text_area("Review/edit your transcribed entry:", key=f"transcript_{n}")
    elif entry_text.strip():
        final_text = entry_text

    st.write("How would you rate your mood right now?")
    rating = st.feedback("faces", key=f"rating_{n}")

    if st.button("Save Entry"):
        if final_text and final_text.strip():
            neg, neu, pos, compound, length = analyze_text(final_text)
            mood_rating = None if rating is None else rating + 1   # faces give 0-4, store 1-5
            add_entry(str(date.today()), final_text, neg, neu, pos, compound, length, mood_rating)
            st.session_state["form_n"] += 1
            st.session_state["just_saved"] = True
            st.rerun()
        else:
            st.warning("Please write or record something first.")

    if st.session_state.pop("just_saved", False):
        st.success("Entry saved!")

# ---------------- RIGHT: trends ----------------
with right:
    st.subheader("Your Trends")
    all_rows = get_all_entries()
    daily = daily_average(get_entries_dataframe(all_rows)) if all_rows else None

    if daily is not None and len(daily) >= 2:
        window_days = st.selectbox(
            "Analysis window",
            [7, 14, 30, 90],
            format_func=lambda d: f"Last {d} days",
        )

        df_window = filter_window(daily, window_days)
        df, slope, volatility = compute_trend(df_window)

        st.line_chart(df.set_index("date")[["compound", "rolling_avg"]])
        st.write(get_trend_summary(df, slope, volatility))

        if volatility is not None:
            st.caption(f"Mood variability (std dev of scores): {volatility:.2f}")

        nudge = get_support_nudge(df)
        if nudge:
            st.info(nudge)

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Negative language")
            st.line_chart(df.set_index("date")[["neg_ratio"]])
        with col_b:
            st.subheader("Weekly summary")
            weekly = weekly_summary(daily)
            st.dataframe(weekly, hide_index=True)
            if len(weekly) >= 2:
                latest, prev = weekly.iloc[-1], weekly.iloc[-2]
                st.metric(
                    "This week's average mood",
                    f"{latest['avg_mood']:.2f}",
                    delta=f"{latest['avg_mood'] - prev['avg_mood']:+.2f} vs last week",
                )
    else:
        st.info("Add entries on at least two different days to start seeing your mood trend.")

# ---------------- BOTTOM: entries ----------------
with st.expander("Your entries"):
    for row in get_all_entries():
        c1, c2 = st.columns([6, 1])
        with c1:
            rated = f" · self-rated: {row[8]}/5" if row[8] else ""
            st.write(f"**{row[1]}** · {row[2].strip()} · score: {row[6]:.2f}{rated}")
        with c2:
            if st.button("Delete", key=f"del_{row[0]}"):
                delete_entry(row[0])
                st.rerun()