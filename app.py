import streamlit as st
from model import predict_proba, simulate_tournament

st.title("🏆 Simulador Mundial 2026")

# ---------------------------
# BRACKET (tu imagen)
# ⚠️ usar nombres EXACTOS del CSV
# ---------------------------
teams = [
    "Germany","Paraguay",
    "France","Sweden",
    "South Africa","Canada",
    "Netherlands","Morocco",
    "Portugal","Croatia",
    "Spain","Austria",
    "United States","Bosnia and Herzegovina",
    "Belgium","Senegal",

    "Brazil","Japan",
    "Ivory Coast","Norway",
    "Mexico","Ecuador",
    "England","DR Congo",
    "Argentina","Cape Verde",
    "Australia","Egypt",
    "Switzerland","Algeria",
    "Colombia","Ghana"
]

# ---------------------------
# PROBABILIDADES PARTIDOS
# ---------------------------
st.subheader("🔮 16avos de final")

for i in range(0, len(teams), 2):
    t1, t2 = teams[i], teams[i+1]
    p = predict_proba(t1, t2)

    st.write(
        f"**{t1} vs {t2}**  \n"
        f"1️⃣ {p['win1']*100:.1f}% | ❌ {p['draw']*100:.1f}% | 2️⃣ {p['win2']*100:.1f}%"
    )

# ---------------------------
# SIMULACIÓN
# ---------------------------
st.subheader("🧠 Simulación del torneo")

n = st.slider("Cantidad de simulaciones", 100, 10000, 2000)

if st.button("Simular Mundial"):
    results = simulate_tournament(teams, n)

    st.subheader("🏆 Probabilidad de ser campeón")

    for team, prob in results.items():
        st.write(f"{team}: {prob*100:.2f}%")

    st.bar_chart(results)
