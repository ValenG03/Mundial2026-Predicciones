import streamlit as st
from model import match_probabilities
import random

st.set_page_config(layout="wide")
st.title("🏆 Mundial 2026 — Bracket Inteligente")

# -----------------------------
# Equipos iniciales
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
# Estado persistente
# -----------------------------
if "current_round" not in st.session_state:
    st.session_state.current_round = teams

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Simular partido (automático)
# -----------------------------
def simulate_match(t1, t2):
    p = match_probabilities(t1, t2)

    # eliminamos empate → lo redistribuimos
    p1 = p["win1"] + p["draw"]/2
    p2 = p["win2"] + p["draw"]/2

    return t1 if random.random() < p1/(p1+p2) else t2

# -----------------------------
# UI partido
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
# Ronda actual
# -----------------------------
round_teams = st.session_state.current_round
next_round = []

st.subheader(f"🔄 Ronda ({len(round_teams)} equipos)")

for i in range(0, len(round_teams), 2):
    t1, t2 = round_teams[i], round_teams[i+1]

    winner = play_match(t1, t2, f"match_{i}")

    if winner:
        next_round.append(winner)

# -----------------------------
# Avanzar manualmente
# -----------------------------
if len(next_round) == len(round_teams)//2:
    if st.button("➡️ Confirmar ganadores de la ronda"):
        st.session_state.history.append(next_round)
        st.session_state.current_round = next_round
        st.rerun()

# -----------------------------
# SIMULAR RESTO
# -----------------------------
if st.button("⚡ Simular resto del torneo"):

    simulated = round_teams.copy()

    while len(simulated) > 1:
        temp = []

        for i in range(0, len(simulated), 2):
            t1, t2 = simulated[i], simulated[i+1]
            winner = simulate_match(t1, t2)
            temp.append(winner)

        simulated = temp

    st.success(f"🏆 Campeón simulado: {simulated[0]}")

# -----------------------------
# Mostrar progreso
# -----------------------------
if st.session_state.history:
    st.subheader("📊 Progreso del torneo")

    for i, rnd in enumerate(st.session_state.history):
        st.write(f"Ronda {i+1}: {', '.join(rnd)}")
