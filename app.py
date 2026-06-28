import streamlit as st
import pandas as pd
from model import train_model

st.title("🏆 FIFA 2026 Predictor (Knockout)")

model, elo = train_model()

teams = list(elo.keys())

team1 = st.selectbox("Equipo 1", teams)
team2 = st.selectbox("Equipo 2", teams)

if st.button("Predecir"):
    e1 = elo.get(team1, 1500)
    e2 = elo.get(team2, 1500)

    X = pd.DataFrame([[e1, e2]], columns=["elo_home", "elo_away"])
    prob = model.predict_proba(X)[0][1]

    st.write(f"Probabilidad de victoria de {team1}: {prob:.2f}")
    st.write(f"Probabilidad de victoria de {team2}: {1 - prob:.2f}")

st.download_button(
    "Descargar dataset",
    data=pd.read_csv("results.csv").to_csv(index=False),
    file_name="results.csv"
)
