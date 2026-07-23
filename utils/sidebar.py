"""Shared sidebar filter component used across all pages."""
from __future__ import annotations

import streamlit as st
import pandas as pd


def render_sidebar_filters(df: pd.DataFrame) -> dict:
    st.sidebar.markdown('<div class="filter-panel-header">FILTERS</div>', unsafe_allow_html=True)

    geography = st.sidebar.multiselect(
        "Country", sorted(df["Geography"].unique()), default=list(df["Geography"].unique())
    )
    gender = st.sidebar.multiselect(
        "Gender", sorted(df["Gender"].unique()), default=list(df["Gender"].unique())
    )
    active = st.sidebar.radio("Membership Status", ["All", "Active", "Inactive"], horizontal=True)

    years = st.sidebar.multiselect(
        "Year", sorted(df["Year"].unique()), default=list(sorted(df["Year"].unique()))
    )

    age_range = st.sidebar.slider(
        "Age", int(df["Age"].min()), int(df["Age"].max()),
        (int(df["Age"].min()), int(df["Age"].max()))
    )
    credit_range = st.sidebar.slider(
        "Credit Score", int(df["CreditScore"].min()), int(df["CreditScore"].max()),
        (int(df["CreditScore"].min()), int(df["CreditScore"].max()))
    )
    balance_range = st.sidebar.slider(
        "Balance (₹)", 0, int(df["Balance_INR"].max()),
        (0, int(df["Balance_INR"].max()))
    )
    salary_range = st.sidebar.slider(
        "Estimated Salary (₹)", int(df["EstimatedSalary_INR"].min()), int(df["EstimatedSalary_INR"].max()),
        (int(df["EstimatedSalary_INR"].min()), int(df["EstimatedSalary_INR"].max()))
    )
    products = st.sidebar.multiselect(
        "Number of Products", sorted(df["NumOfProducts"].unique()),
        default=list(sorted(df["NumOfProducts"].unique()))
    )
    tenure_range = st.sidebar.slider(
        "Tenure (Years)", int(df["Tenure"].min()), int(df["Tenure"].max()),
        (int(df["Tenure"].min()), int(df["Tenure"].max()))
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("European Bank • Customer Analytics")

    return dict(
        geography=geography, gender=gender, active=active, years=years,
        age_range=age_range, credit_range=credit_range, balance_range=balance_range,
        salary_range=salary_range, products=products, tenure_range=tenure_range,
    )
