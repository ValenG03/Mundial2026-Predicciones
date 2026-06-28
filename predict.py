import pickle
import numpy as np

model = pickle.load(open("model.pkl", "rb"))
elo = pickle.load(open("elo.pkl", "rb"))
history = pickle.load(open("history.pkl", "rb"))

def get_recent_stats(team):
    matches = history.get(team, [])[-10:]
    if len(matches) == 0:
        return 0, 0
    goals = np.mean([m[0] for m in matches])
    wins = np.mean([1 if m[0] > m[1] else 0 for m in matches])
    return goals, wins

def predict_match(t1, t2):
    elo_diff = elo.get(t1,1500) - elo.get(t2,1500)

    g1, w1 = get_recent_stats(t1)
    g2, w2 = get_recent_stats(t2)

    X = [[elo_diff, g1 - g2, w1 - w2]]
    pred = model.predict(X)[0]

    return t1 if pred == 1 else t2

# -----------------------------
# Ejemplo: 16avos
# -----------------------------
teams = [
    "Argentina","Mexico","France","USA",
    "Brazil","Germany","Spain","Japan",
    "England","Netherlands","Portugal","Uruguay",
    "Belgium","Croatia","Italy","Denmark"
]

# Eliminación directa
round_teams = teams

while len(round_teams) > 1:
    next_round = []

    for i in range(0, len(round_teams), 2):
        t1 = round_teams[i]
        t2 = round_teams[i+1]

        winner = predict_match(t1, t2)
        print(f"{t1} vs {t2} -> {winner}")
        next_round.append(winner)

    print("-----")
    round_teams = next_round

print("🏆 Campeón:", round_teams[0])

