import streamlit as st
from model import predict_match

st.title("🏆 Predictor Mundial 2026 - 16avos")

# ---------------------------
# PARTIDOS (basados en tu imagen)
# ---------------------------
matches = [
    ("ALE", "PAR"),
    ("FRA", "SUE"),
    ("SUD", "CAN"),
    ("PBJ", "MAR"),
    ("POR", "CRO"),
    ("ESP", "AUT"),
    ("USA", "BYH"),
    ("BEL", "SEN"),

    ("BRA", "JAP"),
    ("CDM", "NOR"),
    ("MEX", "ECU"),
    ("ING", "RDC"),
    ("ARG", "CBV"),
    ("AUS", "EGI"),
    ("SUI", "AGL"),
    ("COL", "GHA"),
]

# ---------------------------
# Mostrar predicciones
# ---------------------------
for t1, t2 in matches:
    probs = predict_match(t1, t2)

    st.write(
        f"**{t1} vs {t2}**  \n"
        f"1️⃣ {probs['team1_win']*100:.1f}% | "
        f"❌ {probs['draw']*100:.1f}% | "
        f"2️⃣ {probs['team2_win']*100:.1f}%"
    )

# ---------------------------
# Descarga CSV
# ---------------------------
import pandas as pd

data = []
for t1, t2 in matches:
    p = predict_match(t1, t2)
    data.append([t1, t2, p['team1_win'], p['draw'], p['team2_win']])

df = pd.DataFrame(data, columns=["Team1", "Team2", "Win1", "Draw", "Win2"])

st.download_button(
    "⬇️ Descargar predicciones",
    df.to_csv(index=False),
    "predicciones.csv",
    "text/csv"
)
