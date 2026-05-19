import pandas as pd
import numpy as np

# =========================
# LOAD DATA
# =========================

df = pd.read_csv(
    "data/processed/economic_risk_dataset.csv"
)

# =========================
# SETTINGS
# =========================

N_SIMULATIONS = 10000
FORECAST_YEARS = 5
BASE_YEAR = df["year"].max()

# =========================
# SORT DATA
# =========================

df = df.sort_values(["country", "year"])

# =========================
# CALCULATE HISTORICAL
# CONSUMPTION GROWTH
# =========================

df["consumption_growth"] = (
    df.groupby("country")["consumption_index"]
    .pct_change()
)

# Remove first null growth rows
growth_data = df.dropna(
    subset=["consumption_growth"]
)

# =========================
# COUNTRY GROWTH STATISTICS
# =========================

growth_stats = (
    growth_data
    .groupby("country")["consumption_growth"]
    .agg(
        mean_growth="mean",
        growth_volatility="std"
    )
    .reset_index()
)

# =========================
# GET LATEST CONSUMPTION
# =========================

latest_consumption = (
    df[df["year"] == BASE_YEAR][[
        "country",
        "consumption_index"
    ]]
)

# =========================
# SIMULATION INPUT TABLE
# =========================

simulation_inputs = pd.merge(
    latest_consumption,
    growth_stats,
    on="country",
    how="inner"
)

# Remove invalid rows
simulation_inputs = simulation_inputs.dropna()

# =========================
# MONTE CARLO SIMULATION
# =========================

results = []

np.random.seed(42)

for _, row in simulation_inputs.iterrows():

    country = row["country"]

    base_consumption = row["consumption_index"]

    mean_growth = row["mean_growth"]

    volatility = row["growth_volatility"]

    for simulation in range(N_SIMULATIONS):

        simulated_consumption = base_consumption

        for step in range(1, FORECAST_YEARS + 1):

            # Random yearly growth shock
            simulated_growth = np.random.normal(
                mean_growth,
                volatility
            )

            # Prevent unrealistic collapse
            simulated_growth = max(
                simulated_growth,
                -0.30
            )

            # Forecast next year
            simulated_consumption = (
                simulated_consumption
                * (1 + simulated_growth)
            )

            results.append({
                "country": country,
                "simulation": simulation,
                "forecast_year": BASE_YEAR + step,
                "simulated_consumption_index": simulated_consumption,
                "simulated_growth": simulated_growth
            })

# =========================
# CREATE RESULTS DATAFRAME
# =========================

simulation_df = pd.DataFrame(results)

# =========================
# SUMMARY STATISTICS
# =========================

summary = (
    simulation_df
    .groupby([
        "country",
        "forecast_year"
    ])["simulated_consumption_index"]
    .agg(
        expected_value="mean",

        downside_5th_percentile=lambda x:
        np.percentile(x, 5),

        upside_95th_percentile=lambda x:
        np.percentile(x, 95),

        median_forecast="median",

        forecast_std="std"
    )
    .reset_index()
)

# =========================
# FORECAST RANGE
# =========================

summary["forecast_range"] = (
    summary["upside_95th_percentile"]
    -
    summary["downside_5th_percentile"]
)

# =========================
# CRISIS PROBABILITY
# =========================

CRISIS_THRESHOLD = 95

crisis_probability = (
    simulation_df
    .groupby([
        "country",
        "forecast_year"
    ])
    .apply(
        lambda x:
        (
            x["simulated_consumption_index"]
            < CRISIS_THRESHOLD
        ).mean()
    )
    .reset_index(name="crisis_probability")
)

summary = pd.merge(
    summary,
    crisis_probability,
    on=["country", "forecast_year"],
    how="left"
)

# =========================
# SAVE OUTPUTS
# =========================

simulation_df.to_csv(
    "data/processed/monte_carlo_simulations.csv",
    index=False
)

summary.to_csv(
    "data/processed/monte_carlo_summary.csv",
    index=False
)

# =========================
# VALIDATION
# =========================

print("\n=== MONTE CARLO SUMMARY ===")
print(summary.head(30))

print("\nSummary statistics:")
print(summary.describe())

print("\nHighest forecast uncertainty:")
print(
    summary.sort_values(
        "forecast_range",
        ascending=False
    ).head(10)
)

print("\nHighest crisis probability:")
print(
    summary.sort_values(
        "crisis_probability",
        ascending=False
    ).head(10)
)

print("\nMonte Carlo simulation completed successfully.")