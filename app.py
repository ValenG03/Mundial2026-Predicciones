import streamlit as st
from model import match_probabilities, simulate_tournament
import pandas as pd

st.title("🏆 Modelo de Predicción y Simulación Mundial 2026")

teams = [
    "Germany","Paraguay","France","Sweden","South Africa","Canada",
    "Netherlands","Morocco","Portugal","Croatia","Spain","Austria",
    "United States","Bosnia and Herzegovina","Belgium","Senegal",
    "Brazil","Japan","Ivory Coast","Norway","Mexico","Ecuador",
    "England","DR Congo","Argentina","Cape Verde","Australia","Egypt",
    "Switzerland","Algeria","Colombia","Ghana"
]

st.subheader("🔮 Probabilidades por partido")

matches = []

for i in range(0, len(teams), 2):
    t1, t2 = teams[i], teams[i+1]
    try:
        p = match_probabilities(t1, t2)
        matches.append({
            "Match": f"{t1} vs {t2}",
            "Team 1": p["win1"],
            "Draw": p["draw"],
            "Team 2": p["win2"]
        })
    except:
        st.error(f"Error en {t1} vs {t2}")

df_matches = pd.DataFrame(matches)
st.dataframe(df_matches)

st.subheader("🧠 Simulación completa")

n = st.slider("Simulaciones", 1000, 50000, 10000)

if st.button("Simular Mundial"):
    results = simulate_tournament(teams, n)

    df = pd.DataFrame(list(results.items()), columns=["Team", "Prob"])
    df = df.sort_values("Prob", ascending=False)

    st.dataframe(df)
    st.bar_chart(df.set_index("Team"))
