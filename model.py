import pandas as pd
import random


def load_results(path="results.csv"):
    df = pd.read_csv(path)

    required_cols = {"home_team", "away_team", "home_score", "away_score"}
    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Faltan columnas en results.csv: {missing}")

    df = df.dropna(subset=["home_team", "away_team", "home_score", "away_score"])

    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce")

    df = df.dropna(subset=["home_score", "away_score"])

    return df


def team_historical_strength(team, df):
    games = df[(df["home_team"] == team) | (df["away_team"] == team)]

    if games.empty:
        return {
            "games": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "win_rate": 0.33,
            "avg_goals_for": 1.0,
            "avg_goals_against": 1.0,
        }

    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0

    for _, row in games.iterrows():
        if row["home_team"] == team:
            gf = row["home_score"]
            ga = row["away_score"]
        else:
            gf = row["away_score"]
            ga = row["home_score"]

        goals_for += gf
        goals_against += ga

        if gf > ga:
            wins += 1
        elif gf == ga:
            draws += 1
        else:
            losses += 1

    total = wins + draws + losses

    return {
        "games": total,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": wins / total if total else 0.33,
        "avg_goals_for": goals_for / total if total else 1.0,
        "avg_goals_against": goals_against / total if total else 1.0,
    }


def head_to_head(team1, team2, df):
    games = df[
        ((df["home_team"] == team1) & (df["away_team"] == team2)) |
        ((df["home_team"] == team2) & (df["away_team"] == team1))
    ]

    wins1 = 0
    wins2 = 0
    draws = 0

    for _, row in games.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        hs = row["home_score"]
        away_score = row["away_score"]

        if hs == away_score:
            draws += 1
        elif hs > away_score:
            if home == team1:
                wins1 += 1
            else:
                wins2 += 1
        else:
            if away == team1:
                wins1 += 1
            else:
                wins2 += 1

    return {
        "games": len(games),
        "wins1": wins1,
        "wins2": wins2,
        "draws": draws,
    }


def match_probabilities(team1, team2, df):
    """
    Calcula la probabilidad estimada de que cada equipo pase de ronda.

    Combina:
    - enfrentamientos directos entre ambos equipos;
    - rendimiento histórico general;
    - goles a favor y goles en contra;
    - suavizado para evitar porcentajes extremos.
    """

    h2h = head_to_head(team1, team2, df)
    s1 = team_historical_strength(team1, df)
    s2 = team_historical_strength(team2, df)

    h2h_weight = min(h2h["games"] / 10, 0.55)
    strength_weight = 1 - h2h_weight

    h2h_total = h2h["wins1"] + h2h["wins2"] + h2h["draws"] + 3

    h2h_p1 = (h2h["wins1"] + 1) / h2h_total
    h2h_p2 = (h2h["wins2"] + 1) / h2h_total
    h2h_draw = (h2h["draws"] + 1) / h2h_total

    attack1 = s1["avg_goals_for"] / max(s2["avg_goals_against"], 0.25)
    attack2 = s2["avg_goals_for"] / max(s1["avg_goals_against"], 0.25)

    score1 = 0.65 * s1["win_rate"] + 0.35 * attack1
    score2 = 0.65 * s2["win_rate"] + 0.35 * attack2

    total_score = score1 + score2

    if total_score == 0:
        strength_p1 = 0.5
        strength_p2 = 0.5
    else:
        strength_p1 = score1 / total_score
        strength_p2 = score2 / total_score

    draw_base = 0.18

    p1 = h2h_weight * h2h_p1 + strength_weight * strength_p1
    p2 = h2h_weight * h2h_p2 + strength_weight * strength_p2
    draw = h2h_weight * h2h_draw + strength_weight * draw_base

    total = p1 + p2 + draw

    p1 = p1 / total
    p2 = p2 / total
    draw = draw / total

    advance1 = p1 + draw / 2
    advance2 = p2 + draw / 2

    return {
        "advance1": advance1,
        "advance2": advance2,
        "draw": draw,
        "h2h_games": h2h["games"],
        "team1_games": s1["games"],
        "team2_games": s2["games"],
    }


def simulate_match(team1, team2, df):
    p = match_probabilities(team1, team2, df)

    if random.random() < p["advance1"]:
        return team1
    return team2
