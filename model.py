import pandas as pd
from xgboost import XGBClassifier

def compute_elo(df, k=20):
    elo = {}
    ratings = []

    for _, row in df.iterrows():
        t1, t2 = row["home_team"], row["away_team"]
        elo.setdefault(t1, 1500)
        elo.setdefault(t2, 1500)

        r1, r2 = elo[t1], elo[t2]
        exp1 = 1 / (1 + 10 ** ((r2 - r1) / 400))

        if row["home_score"] > row["away_score"]:
            score1 = 1
        elif row["home_score"] < row["away_score"]:
            score1 = 0
        else:
            score1 = 0.5

        elo[t1] += k * (score1 - exp1)
        elo[t2] += k * ((1 - score1) - (1 - exp1))

        ratings.append((elo[t1], elo[t2]))

    df["elo_home"], df["elo_away"] = zip(*ratings)
    return df, elo

def train_model():
    df = pd.read_csv("results.csv")

    df = df.dropna(subset=["home_score", "away_score"])
    df["result"] = (df["home_score"] > df["away_score"]).astype(int)

    df, elo = compute_elo(df)

    X = df[["elo_home", "elo_away"]]
    y = df["result"]

    model = XGBClassifier(n_estimators=50, max_depth=3)
    model.fit(X, y)

    return model, elo
