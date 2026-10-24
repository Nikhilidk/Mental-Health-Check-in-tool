"""
Loads made-up demo entries so the dashboard has something to show on a fresh clone.

    python sample_data/load_demo.py          # 3 weeks ending on a recovery
    python sample_data/load_demo.py --low    # same, but the last 3 days are low (shows the support nudge)

All entries and mood ratings below are fictional.
"""
import os
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)            # the database path is relative to the project root
sys.path.insert(0, ROOT)

from database import init_db, add_entry, get_all_entries
from sentiment import analyze_text

# (text, self-rated mood 1-5), oldest first, one entry per day
DEMO = [
    # week 1: mostly steady
    ("Started the week feeling fine. Classes were manageable and I got my notes done.", 4),
    ("Quiet day. Studied for a couple of hours and went for a short walk.", 4),
    ("Tired today, did not sleep well, but I got through my lectures.", 3),
    ("Had a good lab session and enjoyed working with my group.", 5),
    ("Nothing special today. Just routine stuff and some reading.", 3),
    ("Spent the weekend relaxing with family. Felt calm and happy.", 5),
    ("A slow Sunday. Cleaned my room and planned the week.", 4),
    # week 2: stress builds
    ("Assignments are piling up and I feel a bit stressed about deadlines.", 2),
    ("Really rough day. Felt overwhelmed and could not focus on anything.", 1),
    ("Still tired and drained. I barely got any work done today.", 2),
    ("Argued with a friend and felt lonely all evening.", 2),
    ("Slight improvement. Managed to finish one assignment which felt good.", 3),
    ("Ordinary day. Not great, not terrible.", 3),
    ("Felt anxious about the upcoming exams, but talked to a friend and it helped.", 3),
    # week 3: recovery
    ("Made a study plan and it already feels more manageable.", 4),
    ("Good day today. Finished my work early and had time to relax.", 5),
    ("Went out with friends in the evening. Laughed a lot and felt so happy.", 5),
    ("Feeling a bit sleepy but overall fine. Got a lot done.", 4),
    ("Proud of myself for staying on top of things this week.", 5),
    ("Calm and steady day. Enjoyed a long walk and a good meal.", 4),
    ("Feeling hopeful about the exams. Today was a productive day.", 4),
]

# replaces the last three days when --low is passed
LOW_ENDING = [
    ("Feeling hopeless and exhausted again. Everything seems pointless.", 1),
    ("Another rough day. I feel drained and overwhelmed by everything.", 1),
    ("Could not get out of bed. Feeling awful and alone.", 1),
]


def main():
    os.makedirs("data", exist_ok=True)
    init_db()

    if get_all_entries():
        print("data/entries.db already has entries, so nothing was added.")
        print("If it holds real entries, rename it first (e.g. to data/entries_real.db) and run this again.")
        print("Otherwise delete data/entries.db and re-run.")
        return

    entries = list(DEMO)
    if "--low" in sys.argv:
        entries[-3:] = LOW_ENDING

    start = date.today() - timedelta(days=len(entries) - 1)
    for i, (text, rating) in enumerate(entries):
        neg, neu, pos, compound, length = analyze_text(text)
        add_entry(str(start + timedelta(days=i)), text, neg, neu, pos, compound, length, rating)

    print(f"Loaded {len(entries)} demo entries ({start} to {date.today()}).")
    print("Now run: streamlit run app.py")


if __name__ == "__main__":
    main()