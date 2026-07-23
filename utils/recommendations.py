"""Generate rule-based business recommendations from the currently filtered data."""
from __future__ import annotations

import pandas as pd


def generate_recommendations(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No customers match the current filters — widen your selection to see recommendations."]

    recs = []
    churn_rate = df["Exited"].mean() * 100

    if churn_rate > 20:
        recs.append(
            f"Churn rate in this segment is {churn_rate:.1f}%, above the healthy benchmark (~15%). "
            "Prioritize a retention campaign for this segment."
        )

    single_product_churn = df[df["NumOfProducts"] == 1]["Exited"].mean() * 100 if (df["NumOfProducts"] == 1).any() else 0
    if single_product_churn > 25:
        recs.append(
            f"Single-product customers churn at {single_product_churn:.1f}% — cross-sell a second "
            "product (savings, card, or insurance) to increase stickiness."
        )

    inactive_churn = df[df["IsActiveMember"] == 0]["Exited"].mean() * 100 if (df["IsActiveMember"] == 0).any() else 0
    if inactive_churn > 25:
        recs.append(
            f"Inactive members churn at {inactive_churn:.1f}%. Launch a re-engagement flow "
            "(app nudges, relationship-manager outreach) targeting dormant accounts."
        )

    if "Germany" in df["Geography"].values:
        de_rate = df[df["Geography"] == "Germany"]["Exited"].mean() * 100
        if de_rate > churn_rate + 3:
            recs.append(
                f"Germany's churn rate ({de_rate:.1f}%) is notably above the blended average. "
                "Investigate local pricing, service quality, or competitor pressure."
            )

    revenue_at_risk = df.loc[df["Exited"] == 1, "Balance_INR"].sum()
    if revenue_at_risk > 0:
        recs.append(
            f"₹{revenue_at_risk:,.0f} in customer balances has already churned in this segment. "
            "Flag the highest-balance active-at-risk customers for proactive relationship-manager calls."
        )

    high_value_at_risk = df[(df["CustomerValue"].isin(["Gold", "Platinum"])) & (df["ChurnRisk"].isin(["High", "Very High"]))]
    if len(high_value_at_risk) > 0:
        recs.append(
            f"{len(high_value_at_risk)} Gold/Platinum customers are flagged High/Very High churn risk — "
            "these are the highest-priority retention targets by revenue impact."
        )

    if not recs:
        recs.append("This segment looks healthy overall — maintain current engagement and monitor monthly.")

    return recs
