import streamlit as st
import random
from model import match_probabilities

st.set_page_config(layout="wide")

# -----------------------------
# 🎨 ESTILO (FONDO AZUL)
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0a1f44, #0f3c78);
    color: white;
}
button {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🏆 Predictor Mundial 2026")
st.markdown("### 🔮 Elige resultados o simula el torneo completo")

# -----------------------------
# Equipos
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
# Estado
# -----------------------------
if "current_round" not in st.session_state:
    st.session_state.current_round = teams

if "locked_matches" not in st.session_state:
    st.session_state.locked_matches = {}

# -----------------------------
# Simulación condicionada
# -----------------------------
def simulate_tournament_conditional(teams, locked, n=2000):
    wins = {t: 0 for t in teams}

    for _ in range(n):
        sim = teams.copy()
        match_id = 0

        while len(sim) > 1:
            next_round = []

            for i in range(0, len(sim), 2):
                t1, t2 = sim[i], sim[i+1]

                # si el usuario eligió
                if match_id in locked:
                    winner = locked[match_id]
                else:
                    p = match_probabilities(t1, t2)
                    p1 = p["win1"] + p["draw"]/2
                    winner = t1 if random.random() < p1 else t2

                next_round.append(winner)
                match_id += 1

            sim = next_round

        wins[sim[0]] += 1

    return {k: v/n for k, v in wins.items()}

# -----------------------------
# UI PARTIDO
# -----------------------------
def play_match(t1, t2, match_id):
    p = match_probabilities(t1, t2)

    col1, col2, col3 = st.columns([2,1,2])

    with col1:
        if st.button(f"🔥 {t1} ({p['win1']*100:.0f}%)", key=f"{match_id}_1"):
            st.session_state.locked_matches[match_id] = t1

    with col2:
        st.write("⚔️")

    with col3:
        if st.button(f"🔥 {t2} ({p['win2']*100:.0f}%)", key=f"{match_id}_2"):
            st.session_state.locked_matches[match_id] = t2

# -----------------------------
# MOSTRAR RONDA
# -----------------------------
round_teams = st.session_state.current_round
next_round = []
match_id = 0

st.subheader(f"🔵 Ronda actual ({len(round_teams)} equipos)")

for i in range(0, len(round_teams), 2):
    t1, t2 = round_teams[i], round_teams[i+1]

    play_match(t1, t2, match_id)

    if match_id in st.session_state.locked_matches:
        next_round.append(st.session_state.locked_matches[match_id])

    match_id += 1

# -----------------------------
# AVANZAR
# -----------------------------
if len(next_round) == len(round_teams)//2:
    if st.button("➡️ Avanzar ronda"):
        st.session_state.current_round = next_round
        st.rerun()

# -----------------------------
# SIMULAR RESTO
# -----------------------------
if st.button("⚡ Simular resto del torneo"):
    probs = simulate_tournament_conditional(
        teams,
        st.session_state.locked_matches,
        n=3000
    )

    st.subheader("🏆 Probabilidad de campeón (condicionada)")

    # ordenar
    probs = dict(sorted(probs.items(), key=lambda x: x[1], reverse=True))

    for team, p in probs.items():
        emoji = "🥇" if p > 0.2 else "⚽"
        st.write(f"{emoji} {team}: {p*100:.2f}%")

    # campeón más probable
    top = max(probs, key=probs.get)
    st.success(f"🏆 Favorito actual: {top}")
