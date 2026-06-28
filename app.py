import streamlit as st
import pandas as pd

st.title("🏆 FIFA 2026 Predictor")

try:
    df = pd.read_csv("results.csv")
    st.write("✅ Dataset cargado", df.head())

except Exception as e:
    st.error(f"Error cargando dataset: {e}")
    st.stop()

try:
    from model import train_model
    model, elo = train_model()
    st.write("✅ Modelo entrenado")

except Exception as e:
    st.error(f"Error entrenando modelo: {e}")
    st.stop()

teams = list(elo.keys())

team1 = st.selectbox("Equipo 1", teams)
team2 = st.selectbox("Equipo 2", teams)

if st.button("Predecir"):
    try:
        e1 = elo.get(team1, 1500)
        e2 = elo.get(team2, 1500)

        X = pd.DataFrame([[e1, e2]], columns=["elo_home", "elo_away"])
        prob = model.predict_proba(X)[0][1]

        st.success(f"{team1}: {prob:.2f}")
        st.success(f"{team2}: {1 - prob:.2f}")

    except Exception as e:
        st.error(f"Error en predicción: {e}")
