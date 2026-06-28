import streamlit as st
import pandas as pd
from model import load_results, match_probabilities, simulate_match


st.set_page_config(
    page_title="Modelo de Predicción y Simulación Mundial 2026",
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

.center-text {
    text-align: center;
}

.sidebar-title-black {
    color: black;
    font-weight: 900;
    font-size: 24px;
    margin-bottom: 10px;
}

.sidebar-subtitle-black {
    color: black;
    font-weight: 900;
    font-size: 20px;
    margin-top: 10px;
    margin-bottom: 8px;
}

.team-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.13), rgba(255,255,255,0.04));
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.28);
    min-height: 245px;
    width: 100%;
}

.match-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 22px;
    padding: 20px;
    margin-bottom: 22px;
}

.flag-img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 78px;
    height: 52px;
    object-fit: cover;
    border-radius: 10px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.35);
}

.prob-big {
    font-size: 38px;
    font-weight: 900;
    color: #f7c948;
    text-align: center;
    margin-top: 6px;
    margin-bottom: 2px;
}

.prob-label {
    font-size: 14px;
    color: #d8e8ff;
    text-align: center;
    margin-bottom: 8px;
}

.vs-box {
    height: 245px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 4px;
}

.vs-icon {
    font-size: 46px;
    text-align: center;
    line-height: 1;
}

.vs-text {
    font-size: 22px;
    font-weight: 900;
    text-align: center;
    color: white;
    letter-spacing: 1px;
}

.direct-games {
    font-size: 13px;
    color: #d8e8ff;
    text-align: center;
    margin-top: 8px;
}

.winner-box {
    background: linear-gradient(90deg, #f7c948, #f59e0b);
    color: #06172e;
    font-weight: 900;
    border-radius: 16px;
    padding: 10px;
    text-align: center;
    margin-top: 10px;
}

.round-pill {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    font-weight: 900;
    border-radius: 18px;
    padding: 12px 18px;
    text-align: center;
    margin-bottom: 20px;
    font-size: 24px;
}

/* Botones */
.stButton {
    width: 100%;
}

.stButton > button {
    width: 100%;
    min-height: 62px;
    border-radius: 18px !important;
    border: 0px !important;
    font-size: 16px !important;
    font-weight: 900 !important;
    padding: 0.95rem 1rem !important;
    background: linear-gradient(90deg, #00c6ff, #0072ff) !important;
    color: white !important;
    text-align: center !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.30);
}

.stButton > button:hover {
    transform: scale(1.025);
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


flag_codes = {
    "Germany": "de",
    "Paraguay": "py",
    "France": "fr",
    "Sweden": "se",
    "South Africa": "za",
    "Canada": "ca",
    "Netherlands": "nl",
    "Morocco": "ma",
    "Portugal": "pt",
    "Croatia": "hr",
    "Spain": "es",
    "Austria": "at",
    "United States": "us",
    "Bosnia and Herzegovina": "ba",
    "Belgium": "be",
    "Senegal": "sn",
    "Brazil": "br",
    "Japan": "jp",
    "Ivory Coast": "ci",
    "Norway": "no",
    "Mexico": "mx",
    "Ecuador": "ec",
    "England": "gb-eng",
    "DR Congo": "cd",
    "Argentina": "ar",
    "Cape Verde": "cv",
    "Australia": "au",
    "Egypt": "eg",
    "Switzerland": "ch",
    "Algeria": "dz",
    "Colombia": "co",
    "Ghana": "gh"
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

if "champion_probs" not in st.session_state:
    st.session_state.champion_probs = None


# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------
def fmt_pct(x):
    return f"{x * 100:.0f}%"


def get_flag_img(team):
    code = flag_codes.get(team)

    if not code:
        return "https://upload.wikimedia.org/wikipedia/commons/8/8e/Football_%28soccer_ball%29.svg"

    return f"https://flagcdn.com/w160/{code}.png"


def current_match_key(match_index):
    return f"R{st.session_state.round_number}_M{match_index}"


def reset_tournament():
    st.session_state.round_teams = teams.copy()
    st.session_state.round_number = 1
    st.session_state.selected_winners = {}
    st.session_state.history = []
    st.session_state.champion_probs = None


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

    probs = {
        team: count / simulations
        for team, count in champion_counter.items()
        if count > 0
    }

    return dict(sorted(probs.items(), key=lambda x: x[1], reverse=True))


def get_next_round():
    current = st.session_state.round_teams
    winners = []

    for i in range(0, len(current), 2):
        match_key = current_match_key(i // 2)

        if match_key in st.session_state.selected_winners:
            winners.append(st.session_state.selected_winners[match_key])

    return winners


def centered_team_button(team, match_key):
    """
    Centra el bloque completo del botón debajo de la card del equipo.
    La proporción [1.15, 1, 1.15] deja el botón en el centro visual.
    """
    empty_left, button_col, empty_right = st.columns([1.15, 1, 1.15])

    with button_col:
        clicked = st.button(f"Elegir {team}", key=f"btn_{match_key}_{team}")

    return clicked


def show_match(t1, t2, match_index):
    p = match_probabilities(t1, t2, df)
    match_key = current_match_key(match_index)

    selected = st.session_state.selected_winners.get(match_key)

    prob_t1 = p["advance1"]
    prob_t2 = p["advance2"]

    st.markdown('<div class="match-card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2.5, 1, 2.5])

    with col1:
        st.markdown(f"""
        <div class="team-card">
            <img class="flag-img" src="{get_flag_img(t1)}">
            <h3 class="center-text">{t1}</h3>
            <p class="prob-label">Probabilidad estimada de pasar de ronda</p>
            <div class="prob-big">{prob_t1 * 100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

        if centered_team_button(t1, match_key):
            st.session_state.selected_winners[match_key] = t1
            st.session_state.champion_probs = None
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="vs-box">
            <div class="vs-icon">⚔️</div>
            <div class="vs-text">VS</div>
            <div class="direct-games">
                Partidos directos:<br>
                <b>{p["h2h_games"]}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="team-card">
            <img class="flag-img" src="{get_flag_img(t2)}">
            <h3 class="center-text">{t2}</h3>
            <p class="prob-label">Probabilidad estimada de pasar de ronda</p>
            <div class="prob-big">{prob_t2 * 100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

        if centered_team_button(t2, match_key):
            st.session_state.selected_winners[match_key] = t2
            st.session_state.champion_probs = None
            st.rerun()

    if selected:
        st.markdown(
            f'<div class="winner-box">✅ Clasificado elegido: {selected}</div>',
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<h1 class="center-text">🏆 Modelo de Predicción y Simulación Mundial 2026 🏆</h1>
<h3 class="center-text">Elegí tus ganadores y simulá el campeón más probable</h3>
<p class="center-text">⚽ 🔥 🌎 ⭐ 🥅 🏟️</p>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title-black">🎮 Panel del torneo</div>', unsafe_allow_html=True)

    st.write(f"**Fase actual:** {round_names.get(len(st.session_state.round_teams), 'Ronda')}")
    st.write(f"**Equipos vivos:** {len(st.session_state.round_teams)}")
    st.write(f"**Partidos históricos en results.csv:** {len(df)}")

    if st.button("🔄 Reiniciar torneo"):
        reset_tournament()
        st.rerun()

    st.divider()

    st.markdown('<div class="sidebar-subtitle-black">📌 Nota metodológica</div>', unsafe_allow_html=True)

    st.write(
        "Las probabilidades se estiman con resultados históricos. "
        "No representan una predicción perfecta del Mundial 2026, "
        "sino una herramienta interactiva para comparar escenarios."
    )


# --------------------------------------------------
# TORNEO
# --------------------------------------------------
current_teams = st.session_state.round_teams
round_title = round_names.get(len(current_teams), "Ronda")

st.markdown(f'<div class="round-pill">🔵 {round_title}</div>', unsafe_allow_html=True)

if len(current_teams) == 1:
    champion = current_teams[0]

    st.balloons()
    st.success(f"🏆 Campeón elegido: {champion}")

    st.markdown(f"""
    <div class="team-card">
        <img class="flag-img" src="{get_flag_img(champion)}">
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
                st.session_state.champion_probs = None

                st.rerun()
        else:
            st.info("Elegí un ganador en todos los partidos para avanzar.")

    with col_b:
        if st.button("⚡ Simular campeón probable desde esta fase"):
            st.session_state.champion_probs = simulate_remaining_tournament(
                current_teams,
                fixed_winners=st.session_state.selected_winners,
                simulations=3000
            )


# --------------------------------------------------
# PROBABILIDAD DE CAMPEÓN
# --------------------------------------------------
if st.session_state.champion_probs:
    st.divider()
    st.subheader("🏆 Probabilidad de campeón según simulación")

    probs = st.session_state.champion_probs
    top_team = max(probs, key=probs.get)

    st.success(f"🔥 Favorito actual: {top_team} — {fmt_pct(probs[top_team])}")

    chart_df = pd.DataFrame({
        "Equipo": list(probs.keys()),
        "Probabilidad": [v * 100 for v in probs.values()]
    }).sort_values("Probabilidad", ascending=False)

    st.bar_chart(chart_df.set_index("Equipo"))

    st.write("### Top 10 candidatos")

    for team, prob in list(probs.items())[:10]:
        st.write(f"⚽ **{team}**: {prob * 100:.0f}%")


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
                    <img class="flag-img" src="{get_flag_img(winner)}">
                    <p class="center-text"><b>{winner}</b></p>
                </div>
                """, unsafe_allow_html=True)
