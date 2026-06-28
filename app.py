import streamlit as st
import joblib
import os

# asegurar modelo
if not os.path.exists("model.pkl"):
    import model

data = joblib.load("model.pkl")
elo = data["elo"]
model = data["model"]

def predict(team1, team2):
    diff = elo.get(team1, 1500) - elo.get(team2, 1500)
    probs = model.predict_proba([[diff]])[0]
    away, draw, home = probs
    return home, draw, away

st.title("🏆 World Cup 2026 Predictor")

matches = [
    ("France", "Sweden"),
    ("Brazil", "Germany"),
    ("Argentina", "England"),
]

team1, team2 = st.selectbox("Match", matches)

home, draw, away = predict(team1, team2)

st.subheader(f"{team1} vs {team2}")
st.markdown(f"### 1️⃣ {home*100:.1f}% | 🤝 {draw*100:.1f}% | 2️⃣ {away*100:.1f}%")
