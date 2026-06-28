import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier

# ---------------------------
# 1. Cargar datos
# ---------------------------
df = pd.read_csv("results.csv")

# Normalizar columnas
df = df[['date', 'home_team', 'away_team', 'home_score', 'away_score']].dropna()

# ---------------------------
# 2. Feature engineering simple
# ---------------------------
df['goal_diff'] = df['home_score'] - df['away_score']

def result(row):
    if row['goal_diff'] > 0:
        return 1  # gana local
    elif row['goal_diff'] < 0:
        return 2  # gana visitante
    else:
        return 0  # empate

df['result'] = df.apply(result, axis=1)

# ELO simple
elo = {}
K = 20

def get_elo(team):
    return elo.get(team, 1500)

def update_elo(t1, t2, score1):
    r1, r2 = get_elo(t1), get_elo(t2)
    e1 = 1 / (1 + 10 ** ((r2 - r1) / 400))
    elo[t1] = r1 + K * (score1 - e1)
    elo[t2] = r2 + K * ((1 - score1) - (1 - e1))

# Calcular ELO histórico
for _, row in df.iterrows():
    t1, t2 = row['home_team'], row['away_team']
    if row['result'] == 1:
        s1 = 1
    elif row['result'] == 2:
        s1 = 0
    else:
        s1 = 0.5
    update_elo(t1, t2, s1)

# ---------------------------
# 3. Dataset final
# ---------------------------
X = []
y = []

for _, row in df.iterrows():
    t1, t2 = row['home_team'], row['away_team']
    X.append([get_elo(t1), get_elo(t2)])
    y.append(row['result'])

X = np.array(X)
y = np.array(y)

# ---------------------------
# 4. Modelos
# ---------------------------
xgb = XGBClassifier(eval_metric='mlogloss')
rf = RandomForestClassifier()

xgb.fit(X, y)
rf.fit(X, y)

# ---------------------------
# 5. Predicción
# ---------------------------
def predict_match(team1, team2):
    e1, e2 = get_elo(team1), get_elo(team2)
    features = np.array([[e1, e2]])

    p1 = xgb.predict_proba(features)[0]
    p2 = rf.predict_proba(features)[0]

    probs = (p1 + p2) / 2

    return {
        "team1_win": probs[1],
        "draw": probs[0],
        "team2_win": probs[2]
    }
