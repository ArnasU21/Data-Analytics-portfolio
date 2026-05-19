import pandas as pd

# =========================
# DISPLAY SETTINGS
# =========================

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_colwidth", None)

# =========================
# LOAD CLEAN DATASETS
# =========================

inflation = pd.read_csv(
    "data/processed/inflation_clean.csv"
)

unemployment = pd.read_csv(
    "data/processed/unemployment_clean.csv"
)

consumption = pd.read_csv(
    "data/processed/consumption_clean.csv"
)

# =========================
# PREVIEW EACH DATASET
# =========================

print("\n=== INFLATION DATA ===")
print(inflation.to_string())

print("\n=== UNEMPLOYMENT DATA ===")
print(unemployment.to_string())

print("\n=== CONSUMPTION DATA ===")
print(consumption.to_string())

# =========================
# MERGE DATASETS
# =========================

merged = pd.merge(
    inflation,
    unemployment,
    on=["country", "year"],
    how="inner"
)

merged = pd.merge(
    merged,
    consumption,
    on=["country", "year"],
    how="inner"
)

# =========================
# PREVIEW FINAL DATASET
# =========================

print("\n=== FINAL MERGED DATASET ===")
print(merged.to_string())

print("\nDataset Shape:")
print(merged.shape)

# =========================
# SAVE FINAL DATASET
# =========================

merged.to_csv(
    "data/processed/economic_risk_dataset.csv",
    index=False
)

print("\nFinal merged dataset saved successfully.")
