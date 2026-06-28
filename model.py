import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib

# -----------------------
# 1. Load data
# -----------------------
df = pd.read_csv("results.csv")

# basic cleaning
df = df.dropna(subset=["home_team", "away_team", "home_score", "away_score"])

# -----------------------
# 2. Feature engineering (simple ELO-like)
# -----------------------
teams = pd.concat([df["home_team"], df["away_team"]]).unique()
elo = {team: 1500 for team in teams}

def update_elo(home, away, result):
    K = 20
    expected_home = 1 / (1 + 10 ** ((elo[away] - elo[home]) / 400))
    elo[home] += K * (result - expected_home)
    elo[away] += K * ((1 - result) - (1 - expected_home))

features = []
targets = []

for _, row in df.iterrows():
    h, a = row["home_team"], row["away_team"]
    
    diff = elo[h] - elo[a]
    
    # target: 0=away,1=draw,2=home
    if row["home_score"] > row["away_score"]:
        y = 2
        res = 1
    elif row["home_score"] < row["away_score"]:
        y = 0
        res = 0
    else:
        y = 1
        res = 0.5
    
    features.append([diff])
    targets.append(y)

    update_elo(h, a, res)

X = np.array(features)
y = np.array(targets)

# -----------------------
# 3. Models
# -----------------------
rf = RandomForestClassifier(n_estimators=100)
xgb_model = xgb.XGBClassifier(num_class=3, eval_metric="mlogloss")

rf.fit(X, y)
xgb_model.fit(X, y)

# ensemble simple
def predict_proba(diff):
    p1 = rf.predict_proba([[diff]])[0]
    p2 = xgb_model.predict_proba([[diff]])[0]
    return (p1 + p2) / 2

# guardar
joblib.dump((elo, predict_proba), "model.pkl")
