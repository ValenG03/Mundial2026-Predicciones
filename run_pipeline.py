import pandas as pd
from pipeline import run_pipeline

df = pd.read_csv("results.csv")

results = run_pipeline(df)

print("Mejores parámetros:", results["best_params"])
print("Log Loss:", results["log_loss"])
