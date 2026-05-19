import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("data/processed/economic_risk_dataset.csv")

# =========================
# RISK SCORE
# =========================

df["risk_score"] = (
    df["inflation_rate"] * 0.4
    + df["unemployment_rate"] * 0.4
    - df["consumption_index"] * 0.2
)

# =========================
# THEME
# =========================

PURPLE_SCALE = [
    "#F3E8FF",
    "#DDD6FE",
    "#C4B5FD",
    "#A78BFA",
    "#8B5CF6",
    "#6D28D9",
    "#4C1D95",
    "#2E1065"
]

LINE_COLORS = {
    "Inflation Rate": "#2E1065",
    "Unemployment Rate": "#6D28D9",
    "Consumption Index": "#A78BFA",
    "Risk Score": "#4C1D95"
}

TEMPLATE = "plotly_white"

# =========================
# 1. EUROPE CHOROPLETH MAP
# =========================

latest_year = df["year"].max()
latest = df[df["year"] == latest_year]

fig_map = px.choropleth(
    latest,
    locations="country",
    locationmode="country names",
    color="risk_score",
    hover_name="country",
    color_continuous_scale=PURPLE_SCALE,
    title=f"Economic Risk Score by Country ({latest_year})"
)

fig_map.update_geos(
    scope="europe",
    showcountries=True,
    showcoastlines=True,
    showland=True,
    landcolor="#F3F4F6"
)

fig_map.update_layout(
    template=TEMPLATE,
    title_font_size=22,
    margin=dict(l=20, r=20, t=60, b=20)
)

fig_map.show()

# =========================
# 2. CORRELATION HEATMAP
# =========================

corr = df[
    [
        "inflation_rate",
        "unemployment_rate",
        "consumption_index",
        "risk_score"
    ]
].corr()

fig_corr = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale=PURPLE_SCALE,
    title="Correlation Heatmap: Economic Indicators"
)

fig_corr.update_layout(
    template=TEMPLATE,
    title_font_size=22,
    margin=dict(l=40, r=40, t=70, b=40)
)

fig_corr.show()

# =========================
# 3. TIME SERIES TREND
# =========================

yearly = (
    df.groupby("year", as_index=False)[
        [
            "inflation_rate",
            "unemployment_rate",
            "consumption_index",
            "risk_score"
        ]
    ]
    .mean()
)

fig_time = go.Figure()

fig_time.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["inflation_rate"],
        mode="lines+markers",
        name="Inflation Rate",
        line=dict(color=LINE_COLORS["Inflation Rate"], width=3)
    )
)

fig_time.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["unemployment_rate"],
        mode="lines+markers",
        name="Unemployment Rate",
        line=dict(color=LINE_COLORS["Unemployment Rate"], width=3)
    )
)

fig_time.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["consumption_index"],
        mode="lines+markers",
        name="Consumption Index",
        line=dict(color=LINE_COLORS["Consumption Index"], width=3),
        yaxis="y2"
    )
)

fig_time.add_trace(
    go.Scatter(
        x=yearly["year"],
        y=yearly["risk_score"],
        mode="lines+markers",
        name="Risk Score",
        line=dict(color=LINE_COLORS["Risk Score"], width=3, dash="dash")
    )
)

fig_time.update_layout(
    title="Average Economic Indicators Over Time",
    xaxis_title="Year",
    yaxis_title="Inflation / Unemployment / Risk Score",
    yaxis2=dict(
        title="Consumption Index",
        overlaying="y",
        side="right"
    ),
    template=TEMPLATE,
    title_font_size=22,
    legend=dict(
        orientation="h",
        y=-0.25,
        x=0.05
    ),
    margin=dict(l=40, r=40, t=70, b=80)
)

fig_time.show()

# =========================
# 4. RISK RANKING BAR CHART
# =========================

country_risk = (
    df.groupby("country", as_index=False)["risk_score"]
    .mean()
    .sort_values("risk_score", ascending=False)
)

fig_bar = px.bar(
    country_risk,
    x="country",
    y="risk_score",
    color="risk_score",
    color_continuous_scale=PURPLE_SCALE,
    title="Average Economic Risk Score by Country",
    text_auto=".2f"
)

fig_bar.update_layout(
    template=TEMPLATE,
    title_font_size=22,
    xaxis_title="Country",
    yaxis_title="Average Risk Score",
    xaxis_tickangle=-90,
    margin=dict(l=40, r=40, t=70, b=140)
)

fig_bar.show()

# =========================
# SAVE HTML CHARTS
# =========================

fig_map.write_html("economic_risk_map.html")
fig_corr.write_html("correlation_heatmap.html")
fig_time.write_html("economic_indicators_timeseries.html")
fig_bar.write_html("country_risk_ranking.html")

print("Advanced EDA charts created successfully.")
