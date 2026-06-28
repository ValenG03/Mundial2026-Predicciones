import streamlit as st
from model import train_model, predict

st.title("🏆 Predictor Mundial 2026")

model, team_map = train_model()

teams = list(team_map.keys())

team1 = st.selectbox("Equipo 1", teams)
team2 = st.selectbox("Equipo 2", teams)

if st.button("Predecir"):
    prob = predict(model, team_map, team1, team2)
    
    if isinstance(prob, str):
        st.error(prob)
    else:
        st.success(f"Probabilidad de que gane {team1}: {prob:.2f}")
