"""KPI card rendering helpers."""
from __future__ import annotations

import streamlit as st
import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    exited = int(df["Exited"].sum())
    retained = total - exited
    return {
        "Total Customers": f"{total:,}",
        "Churn Rate": f"{(exited / total * 100 if total else 0):.1f}%",
        "Retention Rate": f"{(retained / total * 100 if total else 0):.1f}%",
        "Exited Customers": f"{exited:,}",
        "Avg Credit Score": f"{df['CreditScore'].mean():.0f}" if total else "0",
        "Avg Balance": f"₹{df['Balance_INR'].mean():,.0f}" if total else "₹0",
        "Avg Salary": f"₹{df['EstimatedSalary_INR'].mean():,.0f}" if total else "₹0",
        "Avg Products": f"{df['NumOfProducts'].mean():.2f}" if total else "0",
        "Avg Tenure": f"{df['Tenure'].mean():.1f} yrs" if total else "0 yrs",
        "Active Members": f"{int(df['IsActiveMember'].sum()):,}",
        "Inactive Members": f"{int((df['IsActiveMember'] == 0).sum()):,}",
        "Revenue at Risk": f"₹{df['RevenueRisk'].sum():,.0f}",
        "High Value Customers": f"{int(df['CustomerValue'].isin(['Gold', 'Platinum']).sum()):,}",
    }


def render_kpi_row(kpis: dict, keys: list[str]) -> None:
    cols = st.columns(len(keys))
    for col, key in zip(cols, keys):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{key}</div>
                    <div class="kpi-value">{kpis[key]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
