import pandas as pd
import numpy as np
from xgboost import XGBClassifier

# ---------------------------
# 1. DATA
# ---------------------------
df = pd.read_csv("results.csv")
df = df[['date','home_team','away_team','home_score','away_score']].dropna()
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values("date")

# ---------------------------
# 2. ELO DINÁMICO
# ---------------------------
elo = {}
K = 20

def get_elo(team):
    return elo.get(team, 1500)

def expected(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

def update_elo(t1, t2, s1):
    r1, r2 = get_elo(t1), get_elo(t2)
    e1 = expected(r1, r2)
    elo[t1] = r1 + K * (s1 - e1)
    elo[t2] = r2 + K * ((1 - s1) - (1 - e1))

# construir dataset
X, y = [], []

for _, row in df.iterrows():
    t1, t2 = row['home_team'], row['away_team']

    e1, e2 = get_elo(t1), get_elo(t2)

    # label
    if row['home_score'] > row['away_score']:
        res = 1
        s1 = 1
    elif row['home_score'] < row['away_score']:
        res = 2
        s1 = 0
    else:
        res = 0
        s1 = 0.5

    X.append([e1, e2, e1 - e2])
    y.append(res)

    update_elo(t1, t2, s1)

X = np.array(X)
y = np.array(y)

# ---------------------------
# 3. MODELO
# ---------------------------
model = XGBClassifier(eval_metric="mlogloss")
model.fit(X, y)

# ---------------------------
# 4. PREDICCIÓN
# ---------------------------
def predict_proba(t1, t2):
    e1, e2 = get_elo(t1), get_elo(t2)
    probs = model.predict_proba([[e1, e2, e1 - e2]])[0]

    return {
        "win1": probs[1],
        "draw": probs[0],
        "win2": probs[2]
    }

# ---------------------------
# 5. SIMULACIÓN PARTIDO
# ---------------------------
def simulate_match(t1, t2):
    p = predict_proba(t1, t2)
    r = np.random.rand()

    if r < p["win1"]:
        return t1
    elif r < p["win1"] + p["draw"]:
        return np.random.choice([t1, t2])  # penales
    else:
        return t2

# ---------------------------
# 6. SIMULACIÓN TORNEO
# ---------------------------
def simulate_tournament(bracket, n=1000):
    winners = {}

    for _ in range(n):
        round_teams = bracket[:]

        while len(round_teams) > 1:
            next_round = []
            for i in range(0, len(round_teams), 2):
                winner = simulate_match(round_teams[i], round_teams[i+1])
                next_round.append(winner)
            round_teams = next_round

        champ = round_teams[0]
        winners[champ] = winners.get(champ, 0) + 1

    # probabilidades
    for k in winners:
        winners[k] /= n

    return dict(sorted(winners.items(), key=lambda x: -x[1]))
