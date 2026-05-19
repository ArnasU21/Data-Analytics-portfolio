import pandas as pd
from sklearn.preprocessing import StandardScaler

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("data/processed/economic_risk_dataset.csv")

df = df.dropna()

# =========================
# STANDARDIZE VARIABLES
# =========================

scaler = StandardScaler()

df[[
    "inflation_z",
    "unemployment_z",
    "consumption_z"
]] = scaler.fit_transform(df[[
    "inflation_rate",
    "unemployment_rate",
    "consumption_index"
]])

# =========================
# WEIGHTED RISK SCORE
# =========================

df["risk_score"] = (
    0.30 * df["inflation_z"]
    + 0.50 * df["unemployment_z"]
    - 0.20 * df["consumption_z"]
)

# =========================
# RISK LEVEL CLASSIFICATION
# =========================

def classify_risk(score):
    if score < -0.75:
        return "Low Risk"
    elif score < 0.75:
        return "Medium Risk"
    else:
        return "High Risk"

df["risk_level"] = df["risk_score"].apply(classify_risk)

# =========================
# SAVE SCORED DATA
# =========================

df.to_csv(
    "data/processed/economic_risk_scored.csv",
    index=False
)

# =========================
# VALIDATION
# =========================

print("\n=== SCORED DATA PREVIEW ===")
print(df.head(30))

print("\nRisk score summary:")
print(df["risk_score"].describe())

print("\nRisk level distribution:")
print(df["risk_level"].value_counts())

print("\nAverage risk by country:")
print(
    df.groupby("country")["risk_score"]
    .mean()
    .sort_values(ascending=False)
)

print("\nLatest year risk ranking:")
latest_year = df["year"].max()
print(
    df[df["year"] == latest_year]
    .sort_values("risk_score", ascending=False)
    [["country", "year", "inflation_rate", "unemployment_rate", "consumption_index", "risk_score", "risk_level"]]
)

print("\nEconomic risk scoring completed successfully.")
