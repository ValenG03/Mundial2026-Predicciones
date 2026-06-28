import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -----------------------------
# 1. Cargar dataset
# -----------------------------
df = pd.read_csv("results.csv")
df = df.sort_values("date")

# -----------------------------
# 2. Inicializar ELO
# -----------------------------
elo = {}

def get_elo(team):
    return elo.get(team, 1500)

def update_elo(team1, team2, score1, score2, k=20):
    r1, r2 = get_elo(team1), get_elo(team2)
    expected1 = 1 / (1 + 10 ** ((r2 - r1) / 400))
    
    if score1 > score2:
        s1 = 1
    elif score1 == score2:
        s1 = 0.5
    else:
        s1 = 0

    elo[team1] = r1 + k * (s1 - expected1)
    elo[team2] = r2 + k * ((1 - s1) - (1 - expected1))

# -----------------------------
# 3. Features dinámicos
# -----------------------------
features = []
history = {}

def get_recent_stats(team):
    matches = history.get(team, [])
    last10 = matches[-10:]

    if len(last10) == 0:
        return 0, 0

    goals = np.mean([m[0] for m in last10])
    wins = np.mean([1 if m[0] > m[1] else 0 for m in last10])
    return goals, wins

# -----------------------------
# 4. Construcción dataset ML
# -----------------------------
for _, row in df.iterrows():
    t1 = row["home_team"]
    t2 = row["away_team"]
    g1 = row["home_score"]
    g2 = row["away_score"]

    elo1, elo2 = get_elo(t1), get_elo(t2)
    g_avg1, win1 = get_recent_stats(t1)
    g_avg2, win2 = get_recent_stats(t2)

    X = [
        elo1 - elo2,
        g_avg1 - g_avg2,
        win1 - win2
    ]

    y = 1 if g1 > g2 else 0

    features.append(X + [y])

    # actualizar historial
    history.setdefault(t1, []).append((g1, g2))
    history.setdefault(t2, []).append((g2, g1))

    update_elo(t1, t2, g1, g2)

# -----------------------------
# 5. Train model
# -----------------------------
data = pd.DataFrame(features, columns=["elo_diff", "goal_diff", "win_diff", "target"])

X = data[["elo_diff", "goal_diff", "win_diff"]]
y = data["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = XGBClassifier()
model.fit(X_train, y_train)

preds = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, preds))

# Guardar modelo
import pickle
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(elo, open("elo.pkl", "wb"))
pickle.dump(history, open("history.pkl", "wb"))
