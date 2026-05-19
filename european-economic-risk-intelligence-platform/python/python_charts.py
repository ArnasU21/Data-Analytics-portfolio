import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# EUROPEAN ECONOMIC RISK ANALYSIS - PYTHON HTML CHARTS
# =====================================================

# =====================================================
# LOAD DATA
# =====================================================

risk = pd.read_csv("data/processed/economic_risk_scored.csv")
mc = pd.read_csv("data/processed/monte_carlo_summary.csv")

# =====================================================
# CREATE OUTPUT FOLDER
# =====================================================

os.makedirs("charts", exist_ok=True)

# =====================================================
# THEME - HIGH CONTRAST PURPLE SCALE
# =====================================================

TEMPLATE = "plotly_white"

PURPLE_SCALE = [
    "#D8B4FE",
    "#C084FC",
    "#A855F7",
    "#9333EA",
    "#7E22CE",
    "#581C87",
    "#3B0764"
]

# =====================================================
# MULTI-YEAR AVERAGE DATA
# =====================================================

avg = (
    risk
    .groupby("country", as_index=False)
    .agg(
        risk_score=("risk_score", "mean"),
        inflation_rate=("inflation_rate", "mean"),
        unemployment_rate=("unemployment_rate", "mean"),
        consumption_index=("consumption_index", "mean")
    )
)

avg = avg.sort_values("risk_score", ascending=False).reset_index(drop=True)

RISK_MIN = avg["risk_score"].min()
RISK_MAX = avg["risk_score"].max()

latest_year = risk["year"].max()
latest = risk[risk["year"] == latest_year].copy()

# =====================================================
# COUNTRY LABEL COORDINATES
# =====================================================

country_coords = {
    "Austria": [47.5, 14.5],
    "Belgium": [50.8, 4.5],
    "Bulgaria": [42.7, 25.5],
    "Croatia": [45.1, 15.2],
    "Cyprus": [35.1, 33.4],
    "Czechia": [49.8, 15.5],
    "Denmark": [56.0, 10.0],
    "Estonia": [58.7, 25.0],
    "Finland": [64.5, 26.0],
    "France": [46.5, 2.5],
    "Germany": [51.0, 10.0],
    "Greece": [39.0, 22.0],
    "Hungary": [47.1, 19.5],
    "Ireland": [53.2, -8.0],
    "Italy": [42.8, 12.5],
    "Latvia": [56.9, 24.6],
    "Lithuania": [55.2, 23.9],
    "Netherlands": [52.2, 5.3],
    "Poland": [52.0, 19.0],
    "Portugal": [39.6, -8.0],
    "Romania": [45.9, 24.9],
    "Slovakia": [48.7, 19.5],
    "Slovenia": [46.1, 14.8],
    "Spain": [40.2, -3.7],
    "Sweden": [62.0, 15.0]
}

avg["lat"] = avg["country"].map(lambda x: country_coords.get(x, [None, None])[0])
avg["lon"] = avg["country"].map(lambda x: country_coords.get(x, [None, None])[1])

label_data = avg.dropna(subset=["lat", "lon"]).copy()

label_data["label"] = (
    label_data["country"]
    + "<br>"
    + label_data["risk_score"].round(2).astype(str)
)

# =====================================================
# 1. EUROPEAN RISK MAP - MULTI-YEAR AVERAGE
# =====================================================

fig_map = px.choropleth(
    avg,
    locations="country",
    locationmode="country names",
    color="risk_score",
    hover_name="country",
    hover_data={
        "risk_score": ":.3f",
        "inflation_rate": ":.2f",
        "unemployment_rate": ":.2f",
        "consumption_index": ":.2f",
        "country": False
    },
    color_continuous_scale=PURPLE_SCALE,
    range_color=[RISK_MIN, RISK_MAX],
    title="European Economic Risk Score by Country — Multi-Year Average"
)

fig_map.update_geos(
    scope="europe",
    showcountries=True,
    showcoastlines=True,
    showland=True,
    landcolor="#F3F4F6",
    countrycolor="#FFFFFF",
    coastlinecolor="#9CA3AF",
    projection_type="natural earth",
    lataxis_range=[34, 72],
    lonaxis_range=[-12, 35]
)

fig_map.add_trace(
    go.Scattergeo(
        lon=label_data["lon"],
        lat=label_data["lat"],
        text=label_data["label"],
        mode="text",
        textfont=dict(
            size=10,
            color="#111827",
            family="Arial Black"
        ),
        showlegend=False
    )
)

fig_map.update_layout(
    width=1400,
    height=950,
    paper_bgcolor="white",
    plot_bgcolor="white",
    title=dict(
        x=0.5,
        font=dict(size=30, color="#111827")
    ),
    coloraxis_colorbar=dict(
        title="Risk Score",
        thickness=25,
        len=0.65
    ),
    margin=dict(l=20, r=40, t=90, b=40),
    annotations=[
        dict(
            text="Darker purple indicates higher multi-year economic risk",
            x=0.5,
            y=0.02,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=14, color="#374151")
        )
    ]
)

fig_map.write_html("charts/european_risk_map.html")

# =====================================================
# 2. COUNTRY RISK RANKING - MULTI-YEAR AVERAGE
# =====================================================

country_ranking = avg.sort_values("risk_score", ascending=True)

fig_rank = px.bar(
    country_ranking,
    x="risk_score",
    y="country",
    orientation="h",
    color="risk_score",
    color_continuous_scale=PURPLE_SCALE,
    range_color=[RISK_MIN, RISK_MAX],
    title="Average Economic Risk Score by Country — Multi-Year Average"
)

fig_rank.update_layout(
    template=TEMPLATE,
    height=800,
    title_font_size=24,
    xaxis_title="Average Risk Score",
    yaxis_title="Country",
    coloraxis_colorbar=dict(title="Risk Score")
)

fig_rank.write_html("charts/country_risk_ranking.html")

# =====================================================
# 3. RISK SCORE TREND - TOP 8 MULTI-YEAR RISK COUNTRIES
# =====================================================

top_countries = avg.head(8)["country"].tolist()

trend_data = risk[risk["country"].isin(top_countries)].copy()

fig_trend = px.line(
    trend_data,
    x="year",
    y="risk_score",
    color="country",
    markers=True,
    title="Economic Risk Score Trend — Top 8 High-Risk Countries"
)

fig_trend.update_layout(
    template=TEMPLATE,
    height=650,
    title_font_size=24,
    xaxis_title="Year",
    yaxis_title="Risk Score"
)

fig_trend.write_html("charts/risk_score_trend.html")

# =====================================================
# 4. MACRO STRESS SCATTERPLOT - MULTI-YEAR AVERAGE
# =====================================================

fig_scatter = px.scatter(
    avg,
    x="inflation_rate",
    y="unemployment_rate",
    size="consumption_index",
    color="risk_score",
    hover_name="country",
    color_continuous_scale=PURPLE_SCALE,
    range_color=[RISK_MIN, RISK_MAX],
    title="Macroeconomic Stress Map — Multi-Year Average",
    labels={
        "inflation_rate": "Average Inflation Rate (%)",
        "unemployment_rate": "Average Unemployment Rate (%)",
        "consumption_index": "Average Household Consumption Index",
        "risk_score": "Average Risk Score"
    }
)

fig_scatter.update_layout(
    template=TEMPLATE,
    height=700,
    title_font_size=24,
    coloraxis_colorbar=dict(title="Risk Score")
)

fig_scatter.write_html("charts/macro_stress_scatter.html")

# =====================================================
# 5. MONTE CARLO CONFIDENCE BAND
# =====================================================

country_to_plot = "Greece"

country_mc = mc[mc["country"] == country_to_plot].copy()
country_mc = country_mc.sort_values("forecast_year")

fig_mc = go.Figure()

fig_mc.add_trace(
    go.Scatter(
        x=country_mc["forecast_year"],
        y=country_mc["upside_95th_percentile"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    )
)

fig_mc.add_trace(
    go.Scatter(
        x=country_mc["forecast_year"],
        y=country_mc["downside_5th_percentile"],
        mode="lines",
        fill="tonexty",
        fillcolor="rgba(88, 28, 135, 0.30)",
        line=dict(width=0),
        name="5th–95th Percentile Range"
    )
)

fig_mc.add_trace(
    go.Scatter(
        x=country_mc["forecast_year"],
        y=country_mc["expected_value"],
        mode="lines+markers",
        line=dict(color="#3B0764", width=4),
        marker=dict(size=8),
        name="Expected Forecast"
    )
)

fig_mc.update_layout(
    template=TEMPLATE,
    height=650,
    title=f"Monte Carlo Consumption Forecast — {country_to_plot}",
    title_font_size=24,
    xaxis_title="Forecast Year",
    yaxis_title="Simulated Consumption Index"
)

fig_mc.write_html("charts/monte_carlo_confidence_band.html")

# =====================================================
# 6. CRISIS PROBABILITY RANKING
# =====================================================

latest_forecast_year = mc["forecast_year"].max()

if "crisis_probability" in mc.columns:
    crisis = (
        mc[mc["forecast_year"] == latest_forecast_year]
        .sort_values("crisis_probability", ascending=True)
    )

    fig_crisis = px.bar(
        crisis,
        x="crisis_probability",
        y="country",
        orientation="h",
        color="crisis_probability",
        color_continuous_scale=PURPLE_SCALE,
        range_color=[
            crisis["crisis_probability"].min(),
            crisis["crisis_probability"].max()
        ],
        title=f"Crisis Probability by Country — {latest_forecast_year}"
    )

    fig_crisis.update_layout(
        template=TEMPLATE,
        height=800,
        title_font_size=24,
        xaxis_title="Crisis Probability",
        yaxis_title="Country",
        coloraxis_colorbar=dict(title="Probability")
    )

    fig_crisis.write_html("charts/crisis_probability_ranking.html")

# =====================================================
# 7. FORECAST UNCERTAINTY RANGE
# =====================================================

if "forecast_range" in mc.columns:
    uncertainty = (
        mc[mc["forecast_year"] == latest_forecast_year]
        .sort_values("forecast_range", ascending=True)
    )

    fig_uncertainty = px.bar(
        uncertainty,
        x="forecast_range",
        y="country",
        orientation="h",
        color="forecast_range",
        color_continuous_scale=PURPLE_SCALE,
        range_color=[
            uncertainty["forecast_range"].min(),
            uncertainty["forecast_range"].max()
        ],
        title=f"Forecast Uncertainty Range by Country — {latest_forecast_year}"
    )

    fig_uncertainty.update_layout(
        template=TEMPLATE,
        height=800,
        title_font_size=24,
        xaxis_title="Forecast Range: P95 - P5",
        yaxis_title="Country",
        coloraxis_colorbar=dict(title="Range")
    )

    fig_uncertainty.write_html("charts/forecast_uncertainty_range.html")

print("\nAll HTML charts created successfully in the charts folder.")
