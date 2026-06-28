import streamlit as st
import joblib
import os
import numpy as np

if not os.path.exists("model.pkl"):
    import model

data = joblib.load("model.pkl")

elo = data["elo"]
rf = data["rf"]
xgb_model = data["xgb"]

def predict_proba(diff):
    p1 = rf.predict_proba([[diff]])[0]
    p2 = xgb_model.predict_proba([[diff]])[0]
    return (p1 + p2) / 2

st.title("🏆 FIFA World Cup 2026 Predictor")

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
