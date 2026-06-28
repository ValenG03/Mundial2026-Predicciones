import pandas as pd
from xgboost import XGBClassifier

def load_data():
    df = pd.read_csv("results.csv")
    df = df[['home_team', 'away_team', 'home_score', 'away_score']].dropna()
    
    df['target'] = (df['home_score'] > df['away_score']).astype(int)
    return df

def simple_features(df):
    teams = pd.concat([df['home_team'], df['away_team']]).unique()
    team_map = {team: i for i, team in enumerate(teams)}
    
    df['home_id'] = df['home_team'].map(team_map)
    df['away_id'] = df['away_team'].map(team_map)
    
    return df[['home_id', 'away_id']], df['target'], team_map

def train_model():
    df = load_data()
    X, y, team_map = simple_features(df)
    
    model = XGBClassifier(n_estimators=50, max_depth=4)
    model.fit(X, y)
    
    return model, team_map

def predict(model, team_map, team1, team2):
    if team1 not in team_map or team2 not in team_map:
        return "Equipo desconocido"
    
    X = pd.DataFrame([{
        'home_id': team_map[team1],
        'away_id': team_map[team2]
    }])
    
    prob = model.predict_proba(X)[0][1]
    return prob
