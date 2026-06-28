import pandas as pd
import numpy as np
from itertools import product
from sklearn.isotonic import IsotonicRegression
from scipy.stats import poisson

# ---------------------------
# MÉTRICAS
# ---------------------------
def log_loss(y_true, y_prob):
    eps = 1e-15
    y_prob = np.clip(y_prob, eps, 1 - eps)
    return -np.mean(np.sum(y_true * np.log(y_prob), axis=1))

def brier_score(y_true, y_prob):
    return np.mean(np.sum((y_true - y_prob) ** 2, axis=1))

# ---------------------------
# MODELO BASE
# ---------------------------
class Model:

    def __init__(self, lr=0.05, home_adv=1.1):
        self.lr = lr
        self.home_adv = home_adv
        self.attack = {}
        self.defense = {}
        self.avg_goals = 1.35

    def init_teams(self, teams):
        for t in teams:
            self.attack[t] = 1.0
            self.defense[t] = 1.0

    def expected_goals(self, t1, t2):
        lam1 = self.attack[t1] * self.defense[t2] * self.avg_goals * self.home_adv
        lam2 = self.attack[t2] * self.defense[t1] * self.avg_goals
        return lam1, lam2

    def predict(self, t1, t2):
        lam1, lam2 = self.expected_goals(t1, t2)

        p = np.zeros(3)

        for i in range(6):
            for j in range(6):
                prob = poisson.pmf(i, lam1) * poisson.pmf(j, lam2)

                if i > j:
                    p[0] += prob
                elif j > i:
                    p[2] += prob
                else:
                    p[1] += prob

        return p

    def update(self, t1, t2, g1, g2):
        lam1, lam2 = self.expected_goals(t1, t2)

        err1 = g1 - lam1
        err2 = g2 - lam2

        self.attack[t1] += self.lr * err1
        self.attack[t2] += self.lr * err2
        self.defense[t1] -= self.lr * err2
        self.defense[t2] -= self.lr * err1

# ---------------------------
# PIPELINE
# ---------------------------
def run_pipeline(df):

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values("date")

    # split temporal
    split = int(len(df) * 0.8)
    train = df.iloc[:split]
    test = df.iloc[split:]

    teams = pd.concat([df['home_team'], df['away_team']]).unique()

    best_score = float("inf")
    best_params = None

    # grid search
    for lr, ha in product([0.01, 0.03, 0.05], [1.05, 1.1, 1.2]):

        model = Model(lr=lr, home_adv=ha)
        model.init_teams(teams)

        # entrenar
        for _, r in train.iterrows():
            model.update(r['home_team'], r['away_team'],
                         r['home_score'], r['away_score'])

        # evaluar
        y_true = []
        y_pred = []

        for _, r in test.iterrows():
            p = model.predict(r['home_team'], r['away_team'])

            if r['home_score'] > r['away_score']:
                y = [1,0,0]
            elif r['home_score'] < r['away_score']:
                y = [0,0,1]
            else:
                y = [0,1,0]

            y_true.append(y)
            y_pred.append(p)

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        score = log_loss(y_true, y_pred)

        if score < best_score:
            best_score = score
            best_params = (lr, ha)

    # ---------------------------
    # CALIBRACIÓN
    # ---------------------------
    calibrators = [IsotonicRegression(out_of_bounds='clip') for _ in range(3)]

    for i in range(3):
        calibrators[i].fit(y_pred[:, i], y_true[:, i])

    def calibrated_predict(p):
        return np.array([
            calibrators[i].transform([p[i]])[0] for i in range(3)
        ])

    return {
        "best_params": best_params,
        "log_loss": best_score,
        "calibrator": calibrated_predict
    }
