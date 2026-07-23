"""Reusable Plotly chart builders (enterprise banking theme: white
background, royal blue bars/lines, black labels, light grey grid)."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config.theme import CHART_SEQUENCE, GEO_COLORS, GENDER_COLORS, PLOTLY_TEMPLATE, STATUS_COLORS, TEXT, PRIMARY


def _style(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=12),
        title_font=dict(color=PRIMARY, size=15, family="Inter, Segoe UI, sans-serif"),
        margin=dict(l=10, r=10, t=45, b=10),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                     font=dict(color=TEXT)),
        xaxis=dict(gridcolor="#F0F0F0", linecolor="#D1D5DB", color=TEXT),
        yaxis=dict(gridcolor="#F0F0F0", linecolor="#D1D5DB", color=TEXT),
    )
    return fig


def churn_donut(df: pd.DataFrame) -> go.Figure:
    counts = df["Exited"].map({0: "Retained", 1: "Churned"}).value_counts()
    fig = px.pie(
        names=counts.index, values=counts.values, hole=0.55,
        color=counts.index, color_discrete_map=STATUS_COLORS,
        title="RETENTION VS CHURN",
    )
    fig.update_traces(marker=dict(line=dict(color="#FFFFFF", width=2)))
    return _style(fig, 340)


def churn_by_geography(df: pd.DataFrame) -> go.Figure:
    rate = df.groupby("Geography")["Exited"].mean().mul(100).reset_index()
    fig = px.bar(
        rate, x="Geography", y="Exited", color="Geography",
        color_discrete_map=GEO_COLORS, text_auto=".1f",
        title="CHURN RATE BY GEOGRAPHY (%)", labels={"Exited": "Churn Rate (%)"},
    )
    fig.update_traces(textposition="outside", marker_line_color=PRIMARY, marker_line_width=0.5)
    return _style(fig)


def churn_by_age_group(df: pd.DataFrame) -> go.Figure:
    rate = df.groupby("AgeGroup", observed=True)["Exited"].mean().mul(100).reset_index()
    fig = px.bar(
        rate, x="AgeGroup", y="Exited", text_auto=".1f",
        title="CHURN RATE BY AGE GROUP (%)", color_discrete_sequence=[PRIMARY],
        labels={"Exited": "Churn Rate (%)"},
    )
    fig.update_traces(textposition="outside")
    return _style(fig)


def churn_by_products(df: pd.DataFrame) -> go.Figure:
    rate = df.groupby("NumOfProducts")["Exited"].mean().mul(100).reset_index()
    fig = px.bar(
        rate, x="NumOfProducts", y="Exited", text_auto=".1f",
        title="CHURN RATE BY NUMBER OF PRODUCTS (%)",
        color_discrete_sequence=["#1E40AF"],
        labels={"Exited": "Churn Rate (%)", "NumOfProducts": "Number of Products"},
    )
    fig.update_traces(textposition="outside")
    fig.update_xaxes(type="category")
    return _style(fig)


def gender_churn_grouped(df: pd.DataFrame) -> go.Figure:
    rate = df.groupby(["Geography", "Gender"])["Exited"].mean().mul(100).reset_index()
    fig = px.bar(
        rate, x="Geography", y="Exited", color="Gender", barmode="group",
        color_discrete_map=GENDER_COLORS, text_auto=".1f",
        title="CHURN RATE BY GEOGRAPHY & GENDER (%)", labels={"Exited": "Churn Rate (%)"},
    )
    return _style(fig)


def balance_salary_scatter(df: pd.DataFrame) -> go.Figure:
    sample = df.sample(min(2000, len(df)), random_state=1)
    fig = px.scatter(
        sample, x="Balance_INR", y="EstimatedSalary_INR", color="Exited",
        color_continuous_scale=["#BFDBFE", "#1E40AF"],
        opacity=0.55, title="BALANCE VS SALARY (COLORED BY CHURN)",
        labels={"Exited": "Churned"},
    )
    return _style(fig, 420)

def age_balance_bubble(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("AgeGroup", observed=True).agg(
        AvgBalance=("Balance_INR", "mean"), Count=("CustomerId", "count"),
        ChurnRate=("Exited", "mean"),
    ).reset_index()
    fig = px.scatter(
        agg, x="AgeGroup", y="AvgBalance", size="Count", color="ChurnRate",
        color_continuous_scale="Blues", size_max=55,
        title="AGE GROUP: AVG BALANCE, VOLUME & CHURN RISK",
    )
    fig.update_traces(marker=dict(line=dict(color=PRIMARY, width=1)))
    return _style(fig)


def value_treemap(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby(["Geography", "CustomerValue"], observed=True).size().reset_index(name="Count")
    agg["Geography"] = agg["Geography"].astype(str)
    agg["CustomerValue"] = agg["CustomerValue"].astype(str)
    fig = px.treemap(
        agg, path=["Geography", "CustomerValue"], values="Count",
        color="CustomerValue", color_discrete_sequence=CHART_SEQUENCE,
        title="CUSTOMER VALUE DISTRIBUTION BY GEOGRAPHY",
    )
    fig.update_traces(marker=dict(line=dict(color="#FFFFFF", width=2)),
                       textfont=dict(color="#FFFFFF"))
    return _style(fig, 420)


def credit_score_histogram(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="CreditScore", color="Exited", barmode="overlay", nbins=40,
        color_discrete_map={0: "#BFDBFE", 1: "#1E40AF"},
        title="CREDIT SCORE DISTRIBUTION BY CHURN STATUS",
    )
    return _style(fig)


def tenure_line(df: pd.DataFrame) -> go.Figure:
    rate = df.groupby("Tenure")["Exited"].mean().mul(100).reset_index()
    fig = px.line(
        rate, x="Tenure", y="Exited", markers=True,
        title="CHURN RATE BY TENURE (YEARS)", labels={"Exited": "Churn Rate (%)"},
        color_discrete_sequence=[PRIMARY],
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=8, color=PRIMARY))
    return _style(fig)


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    num_cols = ["CreditScore", "Age", "Tenure", "Balance_INR", "NumOfProducts",
                "HasCrCard", "IsActiveMember", "EstimatedSalary_INR", "Exited"]
    corr = df[num_cols].corr().round(2)
    fig = px.imshow(
        corr, text_auto=True, color_continuous_scale="Blues", zmin=-1, zmax=1,
        title="CORRELATION MATRIX (NUMERIC FEATURES)",
    )
    fig.update_traces(textfont=dict(color=TEXT))
    return _style(fig, 480)


def boxplot_by_churn(df: pd.DataFrame, column: str, title: str) -> go.Figure:
    fig = px.box(
        df, x="Exited", y=column, color="Exited",
        color_discrete_map={0: "#BFDBFE", 1: "#1E40AF"},
        title=title.upper(), labels={"Exited": "Churned"},
    )
    return _style(fig)


def active_member_sunburst(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    d["ActiveLabel"] = d["IsActiveMember"].map({1: "Active", 0: "Inactive"})
    d["ExitedLabel"] = d["Exited"].map({1: "Churned", 0: "Retained"})
    agg = d.groupby(["ActiveLabel", "ExitedLabel"]).size().reset_index(name="Count")
    fig = px.sunburst(
        agg, path=["ActiveLabel", "ExitedLabel"], values="Count",
        color="ExitedLabel", color_discrete_map={"Churned": "#1E40AF", "Retained": "#93C5FD"},
        title="ACTIVE MEMBERSHIP -> CHURN OUTCOME",
    )
    fig.update_traces(marker=dict(line=dict(color="#FFFFFF", width=2)))
    return _style(fig, 420)


def revenue_at_risk_waterfall(df: pd.DataFrame) -> go.Figure:
    by_geo = df[df["Exited"] == 1].groupby("Geography")["Balance_INR"].sum().reset_index()
    fig = go.Figure(go.Waterfall(
        x=by_geo["Geography"], y=by_geo["Balance_INR"],
        connector={"line": {"color": "#D1D5DB"}},
        decreasing={"marker": {"color": PRIMARY}},
        increasing={"marker": {"color": PRIMARY}},
    ))
    fig.update_layout(title="REVENUE AT RISK BY GEOGRAPHY (CHURNED CUSTOMER BALANCES, ₹)")
    return _style(fig)


def churn_gauge(rate_pct: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rate_pct,
        number={"suffix": "%", "font": {"color": TEXT}},
        gauge={
            "axis": {"range": [0, 50], "tickcolor": TEXT},
            "bar": {"color": PRIMARY},
            "bgcolor": "#FFFFFF",
            "bordercolor": PRIMARY,
            "steps": [
                {"range": [0, 15], "color": "#EFF6FF"},
                {"range": [15, 25], "color": "#BFDBFE"},
                {"range": [25, 50], "color": "#93C5FD"},
            ],
        },
        title={"text": "OVERALL CHURN RATE", "font": {"color": PRIMARY}},
    ))
    return _style(fig, 300)
