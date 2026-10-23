import streamlit as st
from datetime import date
from database import init_db, add_entry, get_all_entries, delete_entry
from sentiment import analyze_text
from transcribe import transcribe_audio
from trend import get_entries_dataframe, daily_average, compute_trend, get_trend_summary

init_db()

st.title("Mental Wellness Journal")

st.subheader("Text Entry")
entry_text = st.text_area("How are you feeling today?")

st.subheader("Or record your entry")
audio_value = st.audio_input("Record a voice entry")

final_text = None

# If audio was recorded, transcribe it and show an editable box
if audio_value is not None:
    transcribed = transcribe_audio(audio_value)
    final_text = st.text_area("Review/edit your transcribed entry:", value=transcribed)
elif entry_text.strip():
    final_text = entry_text

if st.button("Save Entry"):
    if final_text and final_text.strip():
        neg, neu, pos, compound, length = analyze_text(final_text)
        add_entry(str(date.today()), final_text, neg, neu, pos, compound, length)
        st.success("Entry saved!")
    else:
        st.warning("Please write or record something first.")

st.subheader("Your Entries So Far")
for row in get_all_entries():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(row)
    with col2:
        if st.button("Delete", key=f"del_{row[0]}"):
            delete_entry(row[0])
            st.rerun()

st.subheader("Your Trends")
all_rows = get_all_entries()

if len(all_rows) >= 2:
    df = get_entries_dataframe(all_rows)
    df = daily_average(df)
    df, slope, volatility = compute_trend(df)

    st.line_chart(df.set_index("date")[["compound", "rolling_avg"]])
    st.write(get_trend_summary(df, slope, volatility))

    if volatility is not None:
        st.caption(f"Mood variability (std dev of scores): {volatility:.2f}")
else:
    st.info("Add a few more entries to start seeing your mood trend.")