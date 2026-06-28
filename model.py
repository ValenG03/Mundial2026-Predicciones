import streamlit as st
import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier

st.title("Predicción partidos - Modelo simple")

# -----------------------------
# 1. Cargar dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("results.csv")
    df = df.sort_values("date")
    return df

df = load_data()

# -----------------------------
# 2. Inicializar ELO
# -----------------------------
elo = {}

def get_elo(team):
    return elo.get(team, 1500)

def update_elo(team1, team2, score1, score2, k=20):
    r1, r2 = get_elo(team1), get_elo(team2)
    expected1 = 1 / (1 + 10 ** ((r2 - r1) / 400))

    s1 = 1 if score1 > score2 else 0 if score1 < score2 else 0.5

    elo[team1] = r1 + k * (s1 - expected1)
    elo[team2] = r2 + k * ((1 - s1) - (1 - expected1))

# -----------------------------
# 3. Features
# -----------------------------
features = []
history = {}

def get_recent_stats(team):
    matches = history.get(team, [])[-10:]
    if not matches:
        return 0, 0
    goals = np.mean([m[0] for m in matches])
    wins = np.mean([1 if m[0] > m[1] else 0 for m in matches])
    return goals, wins

# -----------------------------
# 4. Construcción dataset
# -----------------------------
for _, row in df.iterrows():
    t1, t2 = row["home_team"], row["away_team"]
    g1, g2 = row["home_score"], row["away_score"]

    elo1, elo2 = get_elo(t1), get_elo(t2)
    g_avg1, win1 = get_recent_stats(t1)
    g_avg2, win2 = get_recent_stats(t2)

    X = [elo1 - elo2, g_avg1 - g_avg2, win1 - win2]
    y = 1 if g1 > g2 else 0

    features.append(X + [y])

    history.setdefault(t1, []).append((g1, g2))
    history.setdefault(t2, []).append((g2, g1))

    update_elo(t1, t2, g1, g2)

data = pd.DataFrame(features, columns=["elo_diff", "goal_diff", "win_diff", "target"])

X = data[["elo_diff", "goal_diff", "win_diff"]]
y = data["target"]

# -----------------------------
# 5. Modelo
# -----------------------------
model = XGBClassifier()
model.fit(X, y)

# -----------------------------
# 6. UI simple
# -----------------------------
teams = sorted(set(df["home_team"]).union(set(df["away_team"])))

team1 = st.selectbox("Equipo local", teams)
team2 = st.selectbox("Equipo visitante", teams)

if st.button("Predecir"):
    elo1, elo2 = get_elo(team1), get_elo(team2)
    g1, w1 = get_recent_stats(team1)
    g2, w2 = get_recent_stats(team2)

    X_pred = [[elo1 - elo2, g1 - g2, w1 - w2]]
    pred = model.predict(X_pred)[0]

    if pred == 1:
        st.success(f"Gana {team1}")
    else:
        st.error(f"Gana {team2}")
