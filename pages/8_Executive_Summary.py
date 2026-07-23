import streamlit as st
from config.theme import CUSTOM_CSS
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.kpi_cards import compute_kpis
from utils.recommendations import generate_recommendations

st.set_page_config(page_title="Executive Summary", page_icon=None, layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def get_data():
    return load_and_prepare("data/European_Bank.csv")


df_full = get_data()
filters = render_sidebar_filters(df_full)
df = apply_filters(
    df_full, geography=filters["geography"], gender=filters["gender"], active=filters["active"],
    age_range=filters["age_range"], credit_range=filters["credit_range"],
    balance_range=filters["balance_range"], salary_range=filters["salary_range"],
    products=filters["products"], tenure_range=filters["tenure_range"], years=filters["years"],
)

st.title("EXECUTIVE SUMMARY")
st.caption("Auto-generated summary for stakeholders based on current filters")

kpis = compute_kpis(df)
top_geo = df.groupby("Geography")["Exited"].mean().idxmax() if len(df) else "N/A"
top_geo_rate = df.groupby("Geography")["Exited"].mean().max() * 100 if len(df) else 0

st.markdown(f"""
### Overview

This report covers **{kpis['Total Customers']}** customers in the current filtered view.
The overall churn rate stands at **{kpis['Churn Rate']}**, with a retention rate of **{kpis['Retention Rate']}**.
**{top_geo}** shows the highest churn rate among selected countries at **{top_geo_rate:.1f}%**.

### Key Metrics

| Metric | Value |
|---|---|
| Total Customers | {kpis['Total Customers']} |
| Churn Rate | {kpis['Churn Rate']} |
| Retention Rate | {kpis['Retention Rate']} |
| Average Credit Score | {kpis['Avg Credit Score']} |
| Average Balance | {kpis['Avg Balance']} |
| Average Salary | {kpis['Avg Salary']} |
| High Value Customers | {kpis['High Value Customers']} |
| Revenue at Risk | {kpis['Revenue at Risk']} |
| Active Members | {kpis['Active Members']} |
| Inactive Members | {kpis['Inactive Members']} |

### Business Recommendations
""")

for rec in generate_recommendations(df):
    st.markdown(f"- {rec}")

st.markdown("""
### Conclusion

Churn in this dataset is concentrated among customers who hold a single product,
are not actively engaged, and — geographically — skews higher in Germany. These
factors, combined with the ML-driven feature importance on the Prediction page,
indicate that **product cross-sell and re-engagement of inactive members** are the
two highest-leverage retention levers available to the bank.

*This is a synthetic dataset built to match the project's schema for demonstration
purposes; replace `data/European_Bank.csv` with real, cleaned data for production use.*
""")

st.download_button(
    "Download Filtered Data (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_customer_data.csv",
    mime="text/csv",
)
