import streamlit as st
import pandas as pd
import random
from model import load_results, match_probabilities, simulate_match


st.set_page_config(
    page_title="Predictor Mundial 2026",
    page_icon="🏆",
    layout="wide"
)


# --------------------------------------------------
# ESTILO VISUAL
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #123c69 0%, #06172e 45%, #020817 100%);
    color: white;
}

h1, h2, h3 {
    color: white !important;
}

.team-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.13), rgba(255,255,255,0.04));
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 12px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.28);
}

.match-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 22px;
    padding: 20px;
    margin-bottom: 20px;
}

.big-flag {
    font-size: 42px;
    text-align: center;
}

.prob-text {
    font-size: 15px;
    color: #d8e8ff;
    text-align: center;
}

.center-text {
    text-align: center;
}

.winner-box {
    background: linear-gradient(90deg, #f7c948, #f59e0b);
    color: #06172e;
    font-weight: 800;
    border-radius: 16px;
    padding: 10px;
    text-align: center;
    margin-top: 10px;
}

.stButton > button {
    width: 100%;
    border-radius: 14px !important;
    border: 0px !important;
    font-weight: 700 !important;
    padding: 0.75rem 1rem !important;
    background: linear-gradient(90deg, #00c6ff, #0072ff) !important;
    color: white !important;
}

.stButton > button:hover {
    transform: scale(1.02);
    transition: 0.15s;
    background: linear-gradient(90deg, #f7c948, #f97316) !important;
    color: #06172e !important;
}

[data-testid="stMetricValue"] {
    color: white;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATOS
# --------------------------------------------------
@st.cache_data
def get_data():
    return load_results("results.csv")


df = get_data()


teams = [
    "Germany", "Paraguay",
    "France", "Sweden",
    "South Africa", "Canada",
    "Netherlands", "Morocco",
    "Portugal", "Croatia",
    "Spain", "Austria",
    "United States", "Bosnia and Herzegovina",
    "Belgium", "Senegal",
    "Brazil", "Japan",
    "Ivory Coast", "Norway",
    "Mexico", "Ecuador",
    "England", "DR Congo",
    "Argentina", "Cape Verde",
    "Australia", "Egypt",
    "Switzerland", "Algeria",
    "Colombia", "Ghana"
]


flags = {
    "Germany": "🇩🇪",
    "Paraguay": "🇵🇾",
    "France": "🇫🇷",
    "Sweden": "🇸🇪",
    "South Africa": "🇿🇦",
    "Canada": "🇨🇦",
    "Netherlands": "🇳🇱",
    "Morocco": "🇲🇦",
    "Portugal": "🇵🇹",
    "Croatia": "🇭🇷",
    "Spain": "🇪🇸",
    "Austria": "🇦🇹",
    "United States": "🇺🇸",
    "Bosnia and Herzegovina": "🇧🇦",
    "Belgium": "🇧🇪",
    "Senegal": "🇸🇳",
    "Brazil": "🇧🇷",
    "Japan": "🇯🇵",
    "Ivory Coast": "🇨🇮",
    "Norway": "🇳🇴",
    "Mexico": "🇲🇽",
    "Ecuador": "🇪🇨",
    "England": "🏴",
    "DR Congo": "🇨🇩",
    "Argentina": "🇦🇷",
    "Cape Verde": "🇨🇻",
    "Australia": "🇦🇺",
    "Egypt": "🇪🇬",
    "Switzerland": "🇨🇭",
    "Algeria": "🇩🇿",
    "Colombia": "🇨🇴",
    "Ghana": "🇬🇭"
}


round_names = {
    32: "16avos / Ronda de 32",
    16: "Octavos de final",
    8: "Cuartos de final",
    4: "Semifinales",
    2: "Final",
    1: "Campeón"
}


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "round_teams" not in st.session_state:
    st.session_state.round_teams = teams.copy()

if "round_number" not in st.session_state:
    st.session_state.round_number = 1

if "selected_winners" not in st.session_state:
    st.session_state.selected_winners = {}

if "history" not in st.session_state:
    st.session_state.history = []


# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------
def fmt_pct(x):
    return f"{x * 100:.1f}%"


def get_flag(team):
    return flags.get(team, "⚽")


def current_match_key(match_index):
    return f"R{st.session_state.round_number}_M{match_index}"


def reset_tournament():
    st.session_state.round_teams = teams.copy()
    st.session_state.round_number = 1
    st.session_state.selected_winners = {}
    st.session_state.history = []


def simulate_remaining_tournament(starting_teams, fixed_winners=None, simulations=3000):
    fixed_winners = fixed_winners or {}
    champion_counter = {team: 0 for team in teams}

    for _ in range(simulations):
        current = starting_teams.copy()
        sim_round = st.session_state.round_number

        while len(current) > 1:
            next_round = []

            for i in range(0, len(current), 2):
                t1 = current[i]
                t2 = current[i + 1]
                match_key = f"R{sim_round}_M{i // 2}"

                if match_key in fixed_winners:
                    winner = fixed_winners[match_key]
                else:
                    winner = simulate_match(t1, t2, df)

                next_round.append(winner)

            current = next_round
            sim_round += 1

        champion_counter[current[0]] += 1

    return {
        team: count / simulations
        for team, count in champion_counter.items()
        if count > 0
    }


def show_match(t1, t2, match_index):
    p = match_probabilities(t1, t2, df)
    match_key = current_match_key(match_index)

    selected = st.session_state.selected_winners.get(match_key)

    st.markdown('<div class="match-card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2.5, 1, 2.5])

    with col1:
        st.markdown(f"""
        <div class="team-card">
            <div class="big-flag">{get_flag(t1)}</div>
            <h3 class="center-text">{t1}</h3>
            <p class="prob-text">Gana en 90 min: {fmt_pct(p["win1"])}</p>
            <p class="prob-text">Avanza estimado: {fmt_pct(p["advance1"])}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Elegir {get_flag(t1)} {t1}", key=f"btn_{match_key}_{t1}"):
            st.session_state.selected_winners[match_key] = t1
            st.rerun()

    with col2:
        st.markdown("""
        <br><br>
        <h1 class="center-text">⚔️</h1>
        <p class="center-text">VS</p>
        """, unsafe_allow_html=True)

        st.metric("Empate histórico estimado", fmt_pct(p["draw"]))
        st.caption(f"Partidos directos encontrados: {p['h2h_games']}")

    with col3:
        st.markdown(f"""
        <div class="team-card">
            <div class="big-flag">{get_flag(t2)}</div>
            <h3 class="center-text">{t2}</h3>
            <p class="prob-text">Gana en 90 min: {fmt_pct(p["win2"])}</p>
            <p class="prob-text">Avanza estimado: {fmt_pct(p["advance2"])}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Elegir {get_flag(t2)} {t2}", key=f"btn_{match_key}_{t2}"):
            st.session_state.selected_winners[match_key] = t2
            st.rerun()

    if selected:
        st.markdown(
            f'<div class="winner-box">✅ Clasificado elegido: {get_flag(selected)} {selected}</div>',
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


def get_next_round():
    current = st.session_state.round_teams
    winners = []

    for i in range(0, len(current), 2):
        match_key = current_match_key(i // 2)

        if match_key in st.session_state.selected_winners:
            winners.append(st.session_state.selected_winners[match_key])

    return winners


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<h1 class="center-text">🏆 Predictor Mundial 2026</h1>
<h3 class="center-text">Elegí tus ganadores y simulá el campeón más probable</h3>
<p class="center-text">⚽🔥🌎⭐🥅🏟️</p>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎮 Panel del torneo")
    st.write(f"**Fase actual:** {round_names.get(len(st.session_state.round_teams), 'Ronda')}")
    st.write(f"**Equipos vivos:** {len(st.session_state.round_teams)}")
    st.write(f"**Partidos históricos en results.csv:** {len(df)}")

    if st.button("🔄 Reiniciar torneo"):
        reset_tournament()
        st.rerun()

    st.divider()

    st.subheader("📌 Nota metodológica")
    st.write(
        "Las probabilidades salen de resultados históricos. "
        "No son una predicción perfecta del Mundial 2026: sirven para jugar, comparar y explorar escenarios."
    )


# --------------------------------------------------
# TORNEO
# --------------------------------------------------
current_teams = st.session_state.round_teams
round_title = round_names.get(len(current_teams), "Ronda")

st.subheader(f"🔵 {round_title}")

if len(current_teams) == 1:
    champion = current_teams[0]

    st.balloons()
    st.success(f"🏆 Campeón elegido: {get_flag(champion)} {champion}")

    st.markdown(f"""
    <div class="team-card">
        <div class="big-flag">{get_flag(champion)}</div>
        <h1 class="center-text">🏆 {champion}</h1>
        <h3 class="center-text">Campeón de tu simulación</h3>
    </div>
    """, unsafe_allow_html=True)

else:
    for i in range(0, len(current_teams), 2):
        show_match(current_teams[i], current_teams[i + 1], i // 2)

    next_round = get_next_round()
    total_matches = len(current_teams) // 2

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.write(f"✅ Partidos elegidos: **{len(next_round)} / {total_matches}**")

        if len(next_round) == total_matches:
            if st.button("➡️ Avanzar a la siguiente fase"):
                st.session_state.history.append({
                    "round": round_title,
                    "teams": current_teams.copy(),
                    "winners": next_round.copy()
                })
                st.session_state.round_teams = next_round
                st.session_state.round_number += 1
                st.session_state.selected_winners = {}
                st.rerun()
        else:
            st.info("Elegí un ganador en todos los partidos para avanzar.")

    with col_b:
        if st.button("⚡ Simular campeón probable desde esta fase"):
            probs = simulate_remaining_tournament(
                current_teams,
                fixed_winners=st.session_state.selected_winners,
                simulations=3000
            )

            probs = dict(sorted(probs.items(), key=lambda x: x[1], reverse=True))

            st.session_state["champion_probs"] = probs


# --------------------------------------------------
# PROBABILIDAD DE CAMPEÓN
# --------------------------------------------------
if "champion_probs" in st.session_state:
    st.divider()
    st.subheader("🏆 Probabilidad de campeón según simulación")

    probs = st.session_state["champion_probs"]
    top_team = max(probs, key=probs.get)

    st.success(f"🔥 Favorito actual: {get_flag(top_team)} {top_team} — {fmt_pct(probs[top_team])}")

    chart_df = pd.DataFrame({
        "Equipo": list(probs.keys()),
        "Probabilidad": [v * 100 for v in probs.values()]
    }).sort_values("Probabilidad", ascending=False)

    st.bar_chart(chart_df.set_index("Equipo"))

    for team, prob in list(probs.items())[:10]:
        st.write(f"{get_flag(team)} **{team}**: {prob * 100:.2f}%")


# --------------------------------------------------
# HISTORIAL DE RONDAS
# --------------------------------------------------
if st.session_state.history:
    st.divider()
    st.subheader("📜 Camino elegido")

    for item in st.session_state.history:
        st.write(f"### {item['round']}")
        cols = st.columns(4)

        for idx, winner in enumerate(item["winners"]):
            with cols[idx % 4]:
                st.markdown(f"""
                <div class="team-card">
                    <div class="big-flag">{get_flag(winner)}</div>
                    <p class="center-text"><b>{winner}</b></p>
                </div>
                """, unsafe_allow_html=True)
