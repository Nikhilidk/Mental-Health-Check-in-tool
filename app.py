import streamlit as st
from datetime import date
from database import init_db, add_entry, get_all_entries
from sentiment import analyze_text

init_db()  # ensures table exists every time app runs

st.title("Mental Wellness Journal")

entry_text = st.text_area("How are you feeling today?")

if st.button("Save Entry"):
    if entry_text.strip():
        neg, neu, pos, compound, length = analyze_text(entry_text)
        add_entry(str(date.today()), entry_text, neg, neu, pos, compound, length)
        st.success("Entry saved!")
    else:
        st.warning("Please write something first.")

st.subheader("Your Entries So Far")
for row in get_all_entries():
    st.write(row)