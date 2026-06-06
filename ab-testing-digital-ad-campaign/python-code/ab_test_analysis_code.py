import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from scipy.stats import norm
from statsmodels.stats.proportion import proportions_ztest
from IPython.display import display

# Database connection
load_dotenv()

url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url)

# Ocean Blue Serenity palette
OCEAN_NAVY = "#0B0668"
OCEAN_BLUE = "#0F4C8F"
OCEAN_DEEP = "#0E7DB2"
OCEAN_TEAL = "#1199B8"
OCEAN_CYAN = "#16AEC3"
OCEAN_SKY = "#4EC0D0"
OCEAN_LIGHT = "#89D2DE"
OCEAN_PALE = "#A8DDE6"
OCEAN_ICE = "#C5EAF0"
REFERENCE = "#374151"

GROUP_PALETTE = {
    "ad": OCEAN_NAVY,
    "psa": OCEAN_CYAN
}

sns.set_theme(style="white", context="notebook", font_scale=1.05)
plt.rcParams["axes.grid"] = False

def clean_chart():
    plt.grid(False)
    sns.despine()

def p_label(p_value):
    return "p < 0.001" if p_value < 0.001 else f"p = {p_value:.3f}"

# Main A/B test summary
summary_query = """
SELECT
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    AVG(converted::int) AS conversion_rate
FROM marketing_ab_test
GROUP BY test_group
ORDER BY test_group;
"""

df = pd.read_sql(summary_query, engine)
df["conversion_rate"] = df["conversion_rate"].astype(float)
df["conversion_rate_pct"] = df["conversion_rate"] * 100

display(df)

ad = df[df["test_group"] == "ad"].iloc[0]
psa = df[df["test_group"] == "psa"].iloc[0]

ad_users = int(ad["total_users"])
psa_users = int(psa["total_users"])
ad_conversions = int(ad["conversions"])
psa_conversions = int(psa["conversions"])
ad_rate = float(ad["conversion_rate"])
psa_rate = float(psa["conversion_rate"])

absolute_lift = ad_rate - psa_rate
relative_lift = absolute_lift / psa_rate

z_stat, p_value = proportions_ztest(
    count=[ad_conversions, psa_conversions],
    nobs=[ad_users, psa_users]
)

print("A/B Test Summary")
print("----------------")
print(f"Ad users: {ad_users:,}")
print(f"PSA users: {psa_users:,}")
print(f"Ad conversions: {ad_conversions:,}")
print(f"PSA conversions: {psa_conversions:,}")
print(f"Ad conversion rate: {ad_rate:.2%}")
print(f"PSA conversion rate: {psa_rate:.2%}")
print(f"Absolute lift: {absolute_lift:.2%}")
print(f"Relative lift: {relative_lift:.2%}")
print(f"Z-statistic: {z_stat:.4f}")
print(f"P-value: {p_label(p_value)}")

# Statistical summary table
stats_df = df.copy()
stats_df["std_deviation"] = np.sqrt(
    stats_df["conversion_rate"] * (1 - stats_df["conversion_rate"])
)
stats_df["standard_error"] = stats_df["std_deviation"] / np.sqrt(stats_df["total_users"])
stats_df["ci_lower"] = stats_df["conversion_rate"] - 1.96 * stats_df["standard_error"]
stats_df["ci_upper"] = stats_df["conversion_rate"] + 1.96 * stats_df["standard_error"]
stats_df["ci_lower_pct"] = stats_df["ci_lower"] * 100
stats_df["ci_upper_pct"] = stats_df["ci_upper"] * 100
stats_df["margin_error_pct"] = (
    stats_df["ci_upper"] - stats_df["conversion_rate"]
) * 100

display(stats_df)

ad_row = stats_df[stats_df["test_group"] == "ad"].iloc[0]
psa_row = stats_df[stats_df["test_group"] == "psa"].iloc[0]

difference = ad_row["conversion_rate"] - psa_row["conversion_rate"]
difference_se = np.sqrt(
    ad_row["standard_error"] ** 2 + psa_row["standard_error"] ** 2
)
diff_ci_low = difference - 1.96 * difference_se
diff_ci_high = difference + 1.96 * difference_se

print("\nStatistical Summary")
print("-------------------")
print(f"Ad standard deviation: {ad_row['std_deviation']:.4f}")
print(f"PSA standard deviation: {psa_row['std_deviation']:.4f}")
print(f"Ad standard error: {ad_row['standard_error']:.6f}")
print(f"PSA standard error: {psa_row['standard_error']:.6f}")
print(f"Observed difference: {difference:.2%}")
print(f"Standard error of difference: {difference_se:.4%}")
print(f"95% CI for difference: {diff_ci_low:.2%} to {diff_ci_high:.2%}")

# Chart 1: Users by test group
plt.figure(figsize=(8, 5))
sns.barplot(
    data=df,
    x="test_group",
    y="total_users",
    hue="test_group",
    palette=GROUP_PALETTE,
    legend=False
)
plt.title("Users by Test Group")
plt.xlabel("Test Group")
plt.ylabel("Users")

for i, row in df.iterrows():
    plt.text(i, row["total_users"] + 8000, f"{row['total_users']:,.0f}", ha="center")

clean_chart()
plt.tight_layout()
plt.show()

# Chart 2: Conversion rate by test group
plt.figure(figsize=(8, 5))
sns.barplot(
    data=df,
    x="test_group",
    y="conversion_rate_pct",
    hue="test_group",
    palette=GROUP_PALETTE,
    legend=False
)
plt.title("Conversion Rate by Test Group")
plt.xlabel("Test Group")
plt.ylabel("Conversion Rate (%)")
plt.ylim(0, df["conversion_rate_pct"].max() + 1)

for i, row in df.iterrows():
    plt.text(i, row["conversion_rate_pct"] + 0.1, f"{row['conversion_rate_pct']:.2f}%", ha="center")

clean_chart()
plt.tight_layout()
plt.show()

# Chart 3: Conversion rate with 95% confidence intervals
plt.figure(figsize=(8, 5))
plt.bar(
    stats_df["test_group"],
    stats_df["conversion_rate_pct"],
    yerr=stats_df["margin_error_pct"],
    capsize=8,
    color=[GROUP_PALETTE["ad"], GROUP_PALETTE["psa"]]
)
plt.title("Conversion Rate with 95% Confidence Intervals")
plt.xlabel("Test Group")
plt.ylabel("Conversion Rate (%)")

for i, row in stats_df.iterrows():
    plt.text(
        i,
        row["conversion_rate_pct"] + row["margin_error_pct"] + 0.05,
        f"{row['conversion_rate_pct']:.2f}%",
        ha="center"
    )

clean_chart()
plt.tight_layout()
plt.show()

# Chart 4: Confidence intervals and estimated difference
x_ad = np.linspace(ad_rate - 4 * ad_row["standard_error"], ad_rate + 4 * ad_row["standard_error"], 500)
y_ad = norm.pdf(x_ad, ad_rate, ad_row["standard_error"])

x_psa = np.linspace(psa_rate - 4 * psa_row["standard_error"], psa_rate + 4 * psa_row["standard_error"], 500)
y_psa = norm.pdf(x_psa, psa_rate, psa_row["standard_error"])

x_diff = np.linspace(difference - 4 * difference_se, difference + 4 * difference_se, 500)
y_diff = norm.pdf(x_diff, difference, difference_se)

fig, axes = plt.subplots(
    3,
    1,
    figsize=(11, 8),
    gridspec_kw={"height_ratios": [1, 1, 1.2]}
)

axes[0].plot(x_ad * 100, y_ad, color=OCEAN_NAVY, linewidth=2)
axes[0].fill_between(x_ad * 100, y_ad, color=OCEAN_SKY, alpha=0.55)
axes[0].axvline(ad_rate * 100, color=OCEAN_NAVY, linewidth=2)
axes[0].axvline(ad_row["ci_lower_pct"], color=OCEAN_BLUE, linestyle="--")
axes[0].axvline(ad_row["ci_upper_pct"], color=OCEAN_BLUE, linestyle="--")
axes[0].set_title(
    f"Ad Group Conversion Rate = {ad_rate * 100:.2f}% "
    f"+/- {(1.96 * ad_row['standard_error']) * 100:.2f}%",
    loc="left"
)
axes[0].set_ylabel("Density")

axes[1].plot(x_psa * 100, y_psa, color=OCEAN_CYAN, linewidth=2)
axes[1].fill_between(x_psa * 100, y_psa, color=OCEAN_ICE, alpha=0.75)
axes[1].axvline(psa_rate * 100, color=OCEAN_CYAN, linewidth=2)
axes[1].axvline(psa_row["ci_lower_pct"], color=OCEAN_BLUE, linestyle="--")
axes[1].axvline(psa_row["ci_upper_pct"], color=OCEAN_BLUE, linestyle="--")
axes[1].set_title(
    f"PSA Group Conversion Rate = {psa_rate * 100:.2f}% "
    f"+/- {(1.96 * psa_row['standard_error']) * 100:.2f}%",
    loc="left"
)
axes[1].set_ylabel("Density")

axes[2].plot(x_diff * 100, y_diff, color=OCEAN_TEAL, linewidth=2)
axes[2].fill_between(x_diff * 100, y_diff, color=OCEAN_LIGHT, alpha=0.65)
axes[2].axvline(0, color=REFERENCE, linestyle="--", label="No difference")
axes[2].axvline(difference * 100, color=OCEAN_NAVY, linewidth=2, label="Observed lift")
axes[2].axvline(diff_ci_low * 100, color=OCEAN_BLUE, linestyle="--", label="95% CI")
axes[2].axvline(diff_ci_high * 100, color=OCEAN_BLUE, linestyle="--")
axes[2].set_title(
    f"Difference in Conversion Rates = {difference * 100:.2f}% | "
    f"SE = {difference_se * 100:.4f}% | {p_label(p_value)}",
    loc="left"
)
axes[2].set_xlabel("Conversion Rate / Difference in Conversion Rate (%)")
axes[2].set_ylabel("Density")
axes[2].legend(frameon=False)

for ax in axes:
    ax.grid(False)
    sns.despine(ax=ax)

plt.suptitle("Confidence Intervals and Estimated Difference", fontsize=15, fontweight="bold")
plt.tight_layout()
plt.show()

# Chart 5: Conversion rate by day
day_query = """
SELECT
    most_ads_day,
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    AVG(converted::int) AS conversion_rate
FROM marketing_ab_test
GROUP BY most_ads_day, test_group;
"""

day_df = pd.read_sql(day_query, engine)
day_df["conversion_rate"] = day_df["conversion_rate"].astype(float)
day_df["conversion_rate_pct"] = day_df["conversion_rate"] * 100

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

plt.figure(figsize=(11, 5))
sns.barplot(
    data=day_df,
    x="most_ads_day",
    y="conversion_rate_pct",
    hue="test_group",
    order=day_order,
    palette=GROUP_PALETTE
)
plt.title("Conversion Rate by Most Active Ads Day")
plt.xlabel("Most Active Ads Day")
plt.ylabel("Conversion Rate (%)")
plt.xticks(rotation=30)
plt.legend(title="Test Group", frameon=False)
clean_chart()
plt.tight_layout()
plt.show()

# Chart 6: Conversion rate by hour
hour_query = """
SELECT
    most_ads_hour,
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    AVG(converted::int) AS conversion_rate
FROM marketing_ab_test
GROUP BY most_ads_hour, test_group
ORDER BY most_ads_hour, test_group;
"""

hour_df = pd.read_sql(hour_query, engine)
hour_df["conversion_rate"] = hour_df["conversion_rate"].astype(float)
hour_df["conversion_rate_pct"] = hour_df["conversion_rate"] * 100

plt.figure(figsize=(11, 5))
sns.lineplot(
    data=hour_df,
    x="most_ads_hour",
    y="conversion_rate_pct",
    hue="test_group",
    marker="o",
    palette=GROUP_PALETTE
)
plt.title("Conversion Rate by Most Active Ads Hour")
plt.xlabel("Most Active Ads Hour")
plt.ylabel("Conversion Rate (%)")
plt.legend(title="Test Group", frameon=False)
clean_chart()
plt.tight_layout()
plt.show()

# Chart 7: Conversion rate by ad exposure bucket
exposure_query = """
WITH exposure_buckets AS (
    SELECT
        CASE
            WHEN total_ads BETWEEN 0 AND 10 THEN '0-10 ads'
            WHEN total_ads BETWEEN 11 AND 50 THEN '11-50 ads'
            WHEN total_ads BETWEEN 51 AND 100 THEN '51-100 ads'
            WHEN total_ads BETWEEN 101 AND 200 THEN '101-200 ads'
            ELSE '201+ ads'
        END AS ad_exposure_bucket,
        CASE
            WHEN total_ads BETWEEN 0 AND 10 THEN 1
            WHEN total_ads BETWEEN 11 AND 50 THEN 2
            WHEN total_ads BETWEEN 51 AND 100 THEN 3
            WHEN total_ads BETWEEN 101 AND 200 THEN 4
            ELSE 5
        END AS bucket_order,
        test_group,
        converted
    FROM marketing_ab_test
)
SELECT
    ad_exposure_bucket,
    bucket_order,
    test_group,
    COUNT(*) AS total_users,
    SUM(converted::int) AS conversions,
    AVG(converted::int) AS conversion_rate
FROM exposure_buckets
GROUP BY ad_exposure_bucket, bucket_order, test_group
ORDER BY bucket_order, test_group;
"""

exposure_df = pd.read_sql(exposure_query, engine)
exposure_df["conversion_rate"] = exposure_df["conversion_rate"].astype(float)
exposure_df["conversion_rate_pct"] = exposure_df["conversion_rate"] * 100

bucket_order = ["0-10 ads", "11-50 ads", "51-100 ads", "101-200 ads", "201+ ads"]

plt.figure(figsize=(11, 5))
sns.barplot(
    data=exposure_df,
    x="ad_exposure_bucket",
    y="conversion_rate_pct",
    hue="test_group",
    order=bucket_order,
    palette=GROUP_PALETTE
)
plt.title("Conversion Rate by Ad Exposure Bucket")
plt.xlabel("Ad Exposure Bucket")
plt.ylabel("Conversion Rate (%)")
plt.legend(title="Test Group", frameon=False)
clean_chart()
plt.tight_layout()
plt.show()

# Chart 8: Distribution of total ads seen
ads_query = """
SELECT total_ads
FROM marketing_ab_test;
"""

ads_df = pd.read_sql(ads_query, engine)
ads_cap = ads_df["total_ads"].quantile(0.99)

plt.figure(figsize=(11, 5))
sns.histplot(
    data=ads_df[ads_df["total_ads"] <= ads_cap],
    x="total_ads",
    bins=40,
    color=OCEAN_DEEP
)
plt.title("Distribution of Total Ads Seen")
plt.xlabel("Total Ads Seen, Capped at 99th Percentile")
plt.ylabel("Users")
clean_chart()
plt.tight_layout()
plt.show()