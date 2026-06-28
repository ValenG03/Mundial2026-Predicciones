import pandas as pd
import numpy as np
from scipy.stats import poisson

# ---------------------------
# 1. DATA
# ---------------------------
df = pd.read_csv("results.csv")
df = df[['date','home_team','away_team','home_score','away_score']].dropna()

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values("date")

# ---------------------------
# 2. DECAY TEMPORAL
# ---------------------------
HALF_LIFE = 365 * 2  # 2 años

def time_weight(date, max_date):
    days = (max_date - date).days
    return np.exp(-days / HALF_LIFE)

max_date = df['date'].max()
df['weight'] = df['date'].apply(lambda d: time_weight(d, max_date))

# ---------------------------
# 3. PARAMETROS BASE
# ---------------------------
teams = pd.concat([df['home_team'], df['away_team']]).unique()

attack = {t:1.0 for t in teams}
defense = {t:1.0 for t in teams}

avg_goals = (df['home_score'] + df['away_score']).mean() / 2

# ---------------------------
# 4. ESTIMACIÓN ITERATIVA
# ---------------------------
for _ in range(10):
    for t in teams:
        home = df[df['home_team'] == t]
        away = df[df['away_team'] == t]

        gf = (home['home_score'] * home['weight']).sum() + \
             (away['away_score'] * away['weight']).sum()

        ga = (home['away_score'] * home['weight']).sum() + \
             (away['home_score'] * away['weight']).sum()

        games = home['weight'].sum() + away['weight'].sum()

        if games > 0:
            attack[t] = (gf / games) / avg_goals
            defense[t] = (ga / games) / avg_goals

# ---------------------------
# 5. EXPECTED GOALS
# ---------------------------
HOME_ADV = 1.1

def expected_goals(t1, t2):
    lam1 = attack[t1] * defense[t2] * avg_goals * HOME_ADV
    lam2 = attack[t2] * defense[t1] * avg_goals
    return lam1, lam2

# ---------------------------
# 6. DIXON-COLES AJUSTE
# ---------------------------
def dixon_coles_correction(i, j, lam1, lam2, rho=0.1):
    if i == 0 and j == 0:
        return 1 - (lam1 * lam2 * rho)
    elif i == 0 and j == 1:
        return 1 + lam1 * rho
    elif i == 1 and j == 0:
        return 1 + lam2 * rho
    elif i == 1 and j == 1:
        return 1 - rho
    return 1

# ---------------------------
# 7. PROBABILIDADES PARTIDO
# ---------------------------
def match_probabilities(t1, t2, max_goals=6):
    lam1, lam2 = expected_goals(t1, t2)

    p1 = p2 = draw = 0

    for i in range(max_goals):
        for j in range(max_goals):
            base = poisson.pmf(i, lam1) * poisson.pmf(j, lam2)
            adj = dixon_coles_correction(i, j, lam1, lam2)
            p = base * adj

            if i > j:
                p1 += p
            elif j > i:
                p2 += p
            else:
                draw += p

    return {"win1": p1, "draw": draw, "win2": p2}

# ---------------------------
# 8. SIMULAR PARTIDO
# ---------------------------
def simulate_match(t1, t2):
    lam1, lam2 = expected_goals(t1, t2)

    g1 = poisson.rvs(lam1)
    g2 = poisson.rvs(lam2)

    if g1 > g2:
        return t1
    elif g2 > g1:
        return t2
    else:
        return np.random.choice([t1, t2])  # penales

# ---------------------------
# 9. MONTE CARLO TORNEO
# ---------------------------
def simulate_tournament(bracket, n=10000):
    winners = {}

    for _ in range(n):
        teams = bracket[:]

        while len(teams) > 1:
            next_round = []
            for i in range(0, len(teams), 2):
                w = simulate_match(teams[i], teams[i+1])
                next_round.append(w)
            teams = next_round

        champ = teams[0]
        winners[champ] = winners.get(champ, 0) + 1

    for t in winners:
        winners[t] /= n

    return dict(sorted(winners.items(), key=lambda x: -x[1]))
