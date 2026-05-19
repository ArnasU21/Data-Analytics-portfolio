import pandas as pd

# =========================
# LOAD RAW DATASETS
# =========================

inflation = pd.read_csv("data/raw/inflation_monthly.csv")
unemployment = pd.read_csv("data/raw/unemployment_monthly.csv")
consumption = pd.read_csv("data/raw/household_consumption_quarterly.csv")

# =========================
# COUNTRY MAPPING
# =========================

country_map = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria",
    "HR": "Croatia", "CY": "Cyprus", "CZ": "Czechia",
    "DK": "Denmark", "EE": "Estonia", "FI": "Finland",
    "FR": "France", "DE": "Germany", "EL": "Greece",
    "GR": "Greece", "HU": "Hungary", "IE": "Ireland",
    "IT": "Italy", "LV": "Latvia", "LT": "Lithuania",
    "LU": "Luxembourg", "MT": "Malta", "NL": "Netherlands",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "SK": "Slovakia", "SI": "Slovenia", "ES": "Spain",
    "SE": "Sweden"
}

# =========================
# CLEAN INFLATION
# =========================

inflation = inflation.rename(columns={
    "geo": "country_code",
    "TIME_PERIOD": "date",
    "OBS_VALUE": "inflation_rate"
})

inflation = inflation[["country_code", "date", "inflation_rate"]].copy()
inflation["country"] = inflation["country_code"].map(country_map)
inflation["year"] = inflation["date"].astype(str).str[:4]
inflation["inflation_rate"] = pd.to_numeric(
    inflation["inflation_rate"],
    errors="coerce"
)

inflation_clean = (
    inflation
    .dropna(subset=["country", "year", "inflation_rate"])
    .groupby(["country", "year"], as_index=False)["inflation_rate"]
    .mean()
)

# =========================
# CLEAN UNEMPLOYMENT
# =========================

unemployment = unemployment.rename(columns={
    "geo": "country_code",
    "TIME_PERIOD": "date",
    "OBS_VALUE": "unemployment_rate"
})

# Keep only monthly frequency
if "freq" in unemployment.columns:
    unemployment = unemployment[unemployment["freq"] == "M"]

# Keep only seasonally adjusted data
if "s_adj" in unemployment.columns:
    unemployment = unemployment[unemployment["s_adj"] == "SA"]

# Keep only total age group
if "age" in unemployment.columns:
    unemployment = unemployment[unemployment["age"] == "TOTAL"]

# Keep only total sex, not male/female
if "sex" in unemployment.columns:
    unemployment = unemployment[unemployment["sex"] == "T"]

# Keep unemployment rate as percentage of active population
if "unit" in unemployment.columns:
    unemployment = unemployment[unemployment["unit"] == "PC_ACT"]

unemployment = unemployment[[
    "country_code",
    "date",
    "unemployment_rate"
]].copy()

unemployment["country"] = unemployment["country_code"].map(country_map)
unemployment["year"] = unemployment["date"].astype(str).str[:4]
unemployment["unemployment_rate"] = pd.to_numeric(
    unemployment["unemployment_rate"],
    errors="coerce"
)

unemployment = unemployment.dropna(subset=[
    "country",
    "year",
    "unemployment_rate"
])

# Safety check: remove impossible values
unemployment = unemployment[
    (unemployment["unemployment_rate"] >= 0) &
    (unemployment["unemployment_rate"] <= 40)
]

unemployment_clean = (
    unemployment
    .groupby(["country", "year"], as_index=False)["unemployment_rate"]
    .mean()
)

# =========================
# CLEAN CONSUMPTION
# =========================

consumption = consumption.rename(columns={
    "geo": "country_code",
    "TIME_PERIOD": "date",
    "OBS_VALUE": "consumption_index"
})

consumption = consumption[[
    "country_code",
    "date",
    "consumption_index"
]].copy()

consumption["country"] = consumption["country_code"].map(country_map)
consumption["year"] = consumption["date"].astype(str).str[:4]
consumption["consumption_index"] = pd.to_numeric(
    consumption["consumption_index"],
    errors="coerce"
)

consumption_clean = (
    consumption
    .dropna(subset=["country", "year", "consumption_index"])
    .groupby(["country", "year"], as_index=False)["consumption_index"]
    .mean()
)

# =========================
# SAVE CLEAN FILES
# =========================

inflation_clean.to_csv(
    "data/processed/inflation_clean.csv",
    index=False
)

unemployment_clean.to_csv(
    "data/processed/unemployment_clean.csv",
    index=False
)

consumption_clean.to_csv(
    "data/processed/consumption_clean.csv",
    index=False
)

# =========================
# VALIDATION
# =========================

print("\n=== CLEAN YEARLY INFLATION ===")
print(inflation_clean.head(20))

print("\n=== CLEAN YEARLY UNEMPLOYMENT ===")
print(unemployment_clean.head(20))

print("\n=== CLEAN YEARLY CONSUMPTION ===")
print(consumption_clean.head(20))

print("\n=== UNEMPLOYMENT RANGE CHECK ===")
print(unemployment_clean["unemployment_rate"].describe())

print("\n=== HIGHEST UNEMPLOYMENT VALUES ===")
print(
    unemployment_clean
    .sort_values("unemployment_rate", ascending=False)
    .head(20)
)

print("\n=== DUPLICATE CHECK: UNEMPLOYMENT ===")
print(
    unemployment_clean
    .groupby(["country", "year"])
    .size()
    .reset_index(name="count")
    .query("count > 1")
)

print("\nClean yearly datasets saved successfully.")
