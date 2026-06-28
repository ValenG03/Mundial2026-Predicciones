import streamlit as st
import joblib

st.title("🏆 FIFA World Cup 2026 Predictor")

elo, predict_proba = joblib.load("model.pkl")

# ejemplo fijo (podés expandir a 16avos después)
matches = [
    ("France", "Sweden"),
    ("Brazil", "Germany"),
    ("Argentina", "England"),
]

match = st.selectbox("Select Match", matches)

team1, team2 = match

diff = elo.get(team1, 1500) - elo.get(team2, 1500)
probs = predict_proba(diff)

away, draw, home = probs

st.subheader(f"{team1} vs {team2}")

st.markdown(f"""
### 1️⃣ {home*100:.1f}% | 🤝 {draw*100:.1f}% | 2️⃣ {away*100:.1f}%
""")

st.download_button(
    "Download probabilities",
    data=f"{team1},{team2},{home},{draw},{away}",
    file_name="prediction.csv"
)
