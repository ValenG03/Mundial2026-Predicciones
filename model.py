import pandas as pd
import numpy as np
from scipy.stats import poisson

# ---------------------------
# 1. DATA
# ---------------------------
df = pd.read_csv("results.csv")
df = df[['date','home_team','away_team','home_score','away_score']].dropna()

# ---------------------------
# 2. PARAMETROS GLOBALES
# ---------------------------
avg_goals = df['home_score'].mean()

teams = pd.concat([df['home_team'], df['away_team']]).unique()

attack = {t:1.0 for t in teams}
defense = {t:1.0 for t in teams}

# ---------------------------
# 3. ESTIMAR ATAQUE / DEFENSA
# ---------------------------
for t in teams:
    home = df[df['home_team'] == t]
    away = df[df['away_team'] == t]

    goals_for = home['home_score'].sum() + away['away_score'].sum()
    goals_against = home['away_score'].sum() + away['home_score'].sum()

    games = len(home) + len(away)

    if games > 0:
        attack[t] = goals_for / games / avg_goals
        defense[t] = goals_against / games / avg_goals

# ---------------------------
# 4. EXPECTED GOALS (xG proxy)
# ---------------------------
def expected_goals(t1, t2):
    lam1 = attack[t1] * defense[t2] * avg_goals
    lam2 = attack[t2] * defense[t1] * avg_goals
    return lam1, lam2

# ---------------------------
# 5. SIMULAR PARTIDO
# ---------------------------
def simulate_match(t1, t2):
    lam1, lam2 = expected_goals(t1, t2)

    g1 = poisson.rvs(lam1)
    g2 = poisson.rvs(lam2)

    # knockout → sin empate
    if g1 > g2:
        return t1
    elif g2 > g1:
        return t2
    else:
        return np.random.choice([t1, t2])  # penales

# ---------------------------
# 6. PROBABILIDADES EXACTAS
# ---------------------------
def match_probabilities(t1, t2, max_goals=6):
    lam1, lam2 = expected_goals(t1, t2)

    p1 = p2 = draw = 0

    for i in range(max_goals):
        for j in range(max_goals):
            p = poisson.pmf(i, lam1) * poisson.pmf(j, lam2)

            if i > j:
                p1 += p
            elif j > i:
                p2 += p
            else:
                draw += p

    return {"win1": p1, "draw": draw, "win2": p2}

# ---------------------------
# 7. MONTE CARLO TORNEO
# ---------------------------
def simulate_tournament(bracket, n=5000):
    results = {}

    for _ in range(n):
        teams = bracket[:]

        while len(teams) > 1:
            next_round = []
            for i in range(0, len(teams), 2):
                winner = simulate_match(teams[i], teams[i+1])
                next_round.append(winner)
            teams = next_round

        champ = teams[0]
        results[champ] = results.get(champ, 0) + 1

    for t in results:
        results[t] /= n

    return dict(sorted(results.items(), key=lambda x: -x[1]))
