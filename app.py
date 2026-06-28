import streamlit as st
from model import match_probabilities, simulate_match

st.set_page_config(layout="wide")

st.title("🏆 Mundial 2026 — Simulador Interactivo")

# -----------------------------
# Equipos (16avos)
# -----------------------------
teams = [
    "Germany","Paraguay","France","Sweden","South Africa","Canada",
    "Netherlands","Morocco","Portugal","Croatia","Spain","Austria",
    "United States","Bosnia and Herzegovina","Belgium","Senegal",
    "Brazil","Japan","Ivory Coast","Norway","Mexico","Ecuador",
    "England","DR Congo","Argentina","Cape Verde","Australia","Egypt",
    "Switzerland","Algeria","Colombia","Ghana"
]

# -----------------------------
# Función visual partido
# -----------------------------
def play_match(t1, t2, key):
    p = match_probabilities(t1, t2)

    col1, col2, col3 = st.columns([2,1,2])

    with col1:
        if st.button(f"{t1} ({p['win1']*100:.0f}%)", key=f"{key}_1"):
            return t1

    with col2:
        st.write("VS")

    with col3:
        if st.button(f"{t2} ({p['win2']*100:.0f}%)", key=f"{key}_2"):
            return t2

    return None

# -----------------------------
# RONDA 1
# -----------------------------
st.subheader("🔹 16avos de Final")

winners_16 = []

for i in range(0, len(teams), 2):
    winner = play_match(teams[i], teams[i+1], f"r16_{i}")

    if winner:
        winners_16.append(winner)

# -----------------------------
# RONDA 2
# -----------------------------
if len(winners_16) == 16:
    st.subheader("🔸 Octavos de Final")

    winners_8 = []

    for i in range(0, len(winners_16), 2):
        winner = play_match(winners_16[i], winners_16[i+1], f"r8_{i}")

        if winner:
            winners_8.append(winner)

# -----------------------------
# RONDA 3
# -----------------------------
    if len(winners_8) == 8:
        st.subheader("🔶 Cuartos de Final")

        winners_4 = []

        for i in range(0, len(winners_8), 2):
            winner = play_match(winners_8[i], winners_8[i+1], f"r4_{i}")

            if winner:
                winners_4.append(winner)

# -----------------------------
# SEMIS
# -----------------------------
        if len(winners_4) == 4:
            st.subheader("🔥 Semifinales")

            winners_2 = []

            for i in range(0, len(winners_4), 2):
                winner = play_match(winners_4[i], winners_4[i+1], f"r2_{i}")

                if winner:
                    winners_2.append(winner)

# -----------------------------
# FINAL
# -----------------------------
            if len(winners_2) == 2:
                st.subheader("🏆 Final")

                champion = play_match(winners_2[0], winners_2[1], "final")

                if champion:
                    st.success(f"🏆 Campeón: {champion}")
