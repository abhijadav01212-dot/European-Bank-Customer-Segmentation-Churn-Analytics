"""Data loading, cleaning, and feature-engineering utilities.

All functions are pure (no Streamlit calls) so they can be unit tested and
reused across pages. Caching is applied at the call site in app.py / pages.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config.constants import EUR_TO_INR_RATE

RAW_PATH = "data/European_Bank.csv"


def load_raw(path: str = RAW_PATH) -> pd.DataFrame:
    """Load the raw CSV exactly as provided."""
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the full cleaning checklist from the project spec.

    Steps: missing values, duplicates, unique IDs, drop Surname, standardize
    categoricals, clip out-of-range numerics, enforce binary flags.
    """
    df = df.copy()

    # 1-2. Duplicates
    df = df.drop_duplicates()

    # 3. Unique CustomerId — keep first occurrence
    df = df.drop_duplicates(subset="CustomerId", keep="first")

    # 4. Drop Surname (PII, not needed for analysis)
    if "Surname" in df.columns:
        df = df.drop(columns=["Surname"])

    # 5. Standardize Geography
    df["Geography"] = df["Geography"].astype("string").str.strip().str.title()
    valid_geo = {"France", "Germany", "Spain"}
    df = df[df["Geography"].isin(valid_geo) | df["Geography"].isna()]
    # Fill any remaining missing Geography with the mode
    if df["Geography"].isna().any():
        df["Geography"] = df["Geography"].fillna(df["Geography"].mode()[0])

    # 6. Standardize Gender
    df["Gender"] = df["Gender"].astype("string").str.strip().str.title()

    # 7. CreditScore range + missing value imputation (median)
    df["CreditScore"] = pd.to_numeric(df["CreditScore"], errors="coerce")
    df.loc[(df["CreditScore"] < 300) | (df["CreditScore"] > 900), "CreditScore"] = np.nan
    df["CreditScore"] = df["CreditScore"].fillna(df["CreditScore"].median()).round().astype(int)

    # 8. Age validity
    df = df[(df["Age"] >= 18) & (df["Age"] <= 100)]

    # 9. Tenure validity
    df = df[(df["Tenure"] >= 0) & (df["Tenure"] <= 10)]

    # 10. Balance — negatives to 0
    df["Balance"] = df["Balance"].clip(lower=0)

    # 11. NumOfProducts validity
    df = df[df["NumOfProducts"].between(1, 4)]

    # 12-13. Binary flags
    df = df[df["HasCrCard"].isin([0, 1])]
    df = df[df["IsActiveMember"].isin([0, 1])]

    # 14. Salary negatives
    df = df[df["EstimatedSalary"] >= 0]

    # 15. Exited binary
    df = df[df["Exited"].isin([0, 1])]

    return df.reset_index(drop=True)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create the derived segmentation/analysis columns from the spec.

    Adds Balance_INR / EstimatedSalary_INR as real currency-converted columns
    (source data is in EUR; see config/constants.py::EUR_TO_INR_RATE) and
    bases all downstream segments (BalanceSegment, SalaryGroup, CustomerValue,
    ChurnRisk, RevenueRisk) on the INR values so the whole app is INR-native.
    """
    df = df.copy()
    rate = EUR_TO_INR_RATE

    df["Balance_INR"] = (df["Balance"] * rate).round(2)
    df["EstimatedSalary_INR"] = (df["EstimatedSalary"] * rate).round(2)

    df["AgeGroup"] = pd.cut(
        df["Age"], bins=[17, 25, 35, 45, 55, 65, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]
    )

    bal_bins = [-1, 0, 50000 * rate, 100000 * rate, 150000 * rate, np.inf]
    df["BalanceSegment"] = pd.cut(
        df["Balance_INR"], bins=bal_bins,
        labels=["Zero", "Low (0-55L)", "Medium (55L-1.1Cr)", "High (1.1-1.65Cr)", "Very High (1.65Cr+)"]
    )

    df["CreditScoreBand"] = pd.cut(
        df["CreditScore"], bins=[299, 579, 669, 739, 799, 900],
        labels=["Poor", "Fair", "Good", "Very Good", "Excellent"]
    )

    df["TenureGroup"] = pd.cut(
        df["Tenure"], bins=[-1, 2, 5, 8, 10],
        labels=["New (0-2y)", "Established (3-5y)", "Loyal (6-8y)", "Veteran (9-10y)"]
    )

    df["SalaryGroup"] = pd.qcut(
        df["EstimatedSalary_INR"], q=4,
        labels=["Low", "Medium", "High", "Very High"]
    )

    # CustomerValue: composite of balance, salary, products, tenure
    # (normalization makes this scale-invariant, so EUR vs INR gives the
    # same tiers — using the INR columns keeps everything consistent)
    norm_balance = (df["Balance_INR"] - df["Balance_INR"].min()) / (
        df["Balance_INR"].max() - df["Balance_INR"].min() + 1e-9
    )
    norm_salary = (df["EstimatedSalary_INR"] - df["EstimatedSalary_INR"].min()) / (
        df["EstimatedSalary_INR"].max() - df["EstimatedSalary_INR"].min() + 1e-9
    )
    value_score = (
        0.45 * norm_balance + 0.30 * norm_salary
        + 0.15 * (df["NumOfProducts"] / 4) + 0.10 * (df["Tenure"] / 10)
    )
    df["CustomerValue"] = pd.cut(
        value_score, bins=[-0.01, 0.25, 0.5, 0.75, 1.0],
        labels=["Bronze", "Silver", "Gold", "Platinum"]
    )

    # RevenueRisk = potential balance (INR) lost if a customer churns
    df["RevenueRisk"] = np.where(df["Exited"] == 1, df["Balance_INR"], 0)

    # EngagementScore: active membership + credit card + products, 0-100
    df["EngagementScore"] = (
        df["IsActiveMember"] * 40
        + df["HasCrCard"] * 20
        + (df["NumOfProducts"].clip(upper=2) / 2) * 40
    ).round(1)

    # ChurnRisk: simple weighted heuristic (independent of the ML model),
    # used for quick-scan business flags on the dashboard
    risk = (
        (df["IsActiveMember"] == 0).astype(int) * 30
        + (df["NumOfProducts"] == 1).astype(int) * 20
        + (df["Age"] > 50).astype(int) * 20
        + (df["Geography"] == "Germany").astype(int) * 15
        + (df["Balance_INR"] > 150000 * rate).astype(int) * 15
    )
    df["ChurnRisk"] = pd.cut(
        risk, bins=[-1, 20, 40, 60, 100],
        labels=["Low", "Medium", "High", "Very High"]
    )

    # Final column order matching the required project schema, with the
    # extra app-internal columns (RevenueRisk, EngagementScore, ChurnRisk)
    # appended at the end since the dashboard/pages depend on them.
    schema_order = [
        "Year", "CustomerId", "CreditScore", "CreditScoreBand", "Geography", "Gender",
        "Age", "AgeGroup", "Tenure", "TenureGroup", "Balance", "Balance_INR", "BalanceSegment",
        "NumOfProducts", "HasCrCard", "IsActiveMember", "EstimatedSalary", "EstimatedSalary_INR",
        "SalaryGroup", "CustomerValue", "Exited",
    ]
    extra_cols = ["RevenueRisk", "EngagementScore", "ChurnRisk"]
    df = df[schema_order + extra_cols]

    return df


def load_and_prepare(path: str = RAW_PATH) -> pd.DataFrame:
    """Convenience wrapper: raw -> clean -> engineered."""
    return engineer_features(clean_data(load_raw(path)))


def apply_filters(
    df: pd.DataFrame,
    geography=None, gender=None, active=None,
    age_range=None, credit_range=None, balance_range=None,
    salary_range=None, products=None, tenure_range=None, years=None,
) -> pd.DataFrame:
    """Apply the sidebar filter set. Any None/empty selection is ignored."""
    out = df
    if geography:
        out = out[out["Geography"].isin(geography)]
    if gender:
        out = out[out["Gender"].isin(gender)]
    if active is not None and active != "All":
        out = out[out["IsActiveMember"] == (1 if active == "Active" else 0)]
    if age_range:
        out = out[out["Age"].between(*age_range)]
    if credit_range:
        out = out[out["CreditScore"].between(*credit_range)]
    if balance_range:
        out = out[out["Balance_INR"].between(*balance_range)]
    if salary_range:
        out = out[out["EstimatedSalary_INR"].between(*salary_range)]
    if products:
        out = out[out["NumOfProducts"].isin(products)]
    if tenure_range:
        out = out[out["Tenure"].between(*tenure_range)]
    if years:
        out = out[out["Year"].isin(years)]
    return out
