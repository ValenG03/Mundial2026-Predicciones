import streamlit as st
from model import match_probabilities, simulate_tournament

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

for i in range(0, len(teams), 2):
    t1, t2 = teams[i], teams[i+1]
    p = match_probabilities(t1, t2)

    st.write(
        f"{t1} vs {t2} → "
        f"{p['win1']*100:.1f}% | "
        f"{p['draw']*100:.1f}% | "
        f"{p['win2']*100:.1f}%"
    )

st.subheader("🧠 Simulación completa")

n = st.slider("Simulaciones", 1000, 50000, 10000)

if st.button("Simular Mundial"):
    results = simulate_tournament(teams, n)

    st.subheader("🏆 Probabilidad de campeón")

    for t, p in results.items():
        st.write(f"{t}: {p*100:.2f}%")

    st.bar_chart(results)
