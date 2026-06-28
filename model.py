import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# cargar datos
df = pd.read_csv("results.csv")
df = df.dropna(subset=["home_team", "away_team", "home_score", "away_score"])

# ELO simple
teams = pd.concat([df["home_team"], df["away_team"]]).unique()
elo = {team: 1500 for team in teams}

def update_elo(h, a, res):
    K = 20
    exp = 1 / (1 + 10 ** ((elo[a] - elo[h]) / 400))
    elo[h] += K * (res - exp)
    elo[a] += K * ((1 - res) - (1 - exp))

X, y = [], []

for _, r in df.iterrows():
    h, a = r["home_team"], r["away_team"]
    diff = elo[h] - elo[a]

    if r["home_score"] > r["away_score"]:
        y.append(2); res = 1
    elif r["home_score"] < r["away_score"]:
        y.append(0); res = 0
    else:
        y.append(1); res = 0.5

    X.append([diff])
    update_elo(h, a, res)

# modelo
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# guardar TODO
joblib.dump({
    "elo": elo,
    "model": model
}, "model.pkl")
