"""Customer Segmentation & Churn Pattern Analytics — European Banking.

Entry point / Home page. Loads and caches data, applies theme, renders the
landing view with top-level KPIs and navigation guidance.
"""
import streamlit as st
import pandas as pd

from config.theme import CUSTOM_CSS
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.kpi_cards import compute_kpis, render_kpi_row
from utils.charts import churn_donut, churn_gauge
from utils.recommendations import generate_recommendations

st.set_page_config(
    page_title="European Bank | Churn Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading and cleaning customer data…")
def get_data() -> pd.DataFrame:
    return load_and_prepare("data/European_Bank.csv")


df_full = get_data()

st.title("CUSTOMER SEGMENTATION & CHURN PATTERN ANALYTICS")
st.caption("European Banking · Interactive Business Intelligence Dashboard")

filters = render_sidebar_filters(df_full)
df = apply_filters(
    df_full,
    geography=filters["geography"], gender=filters["gender"], active=filters["active"],
    age_range=filters["age_range"], credit_range=filters["credit_range"],
    balance_range=filters["balance_range"], salary_range=filters["salary_range"],
    products=filters["products"], tenure_range=filters["tenure_range"], years=filters["years"],
)

st.session_state["filtered_df"] = df  # shared across pages via session state

st.markdown("### KEY PERFORMANCE INDICATORS")
kpis = compute_kpis(df)
render_kpi_row(kpis, ["Total Customers", "Churn Rate", "Retention Rate", "Revenue at Risk"])
st.write("")
render_kpi_row(kpis, ["Avg Credit Score", "Avg Balance", "Avg Products", "Active Members"])

st.write("")
col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(churn_donut(df), use_container_width=True)
with col2:
    st.plotly_chart(churn_gauge(df["Exited"].mean() * 100 if len(df) else 0), use_container_width=True)

st.markdown("### RECOMMENDATIONS")
for rec in generate_recommendations(df):
    st.info(rec)

st.markdown("---")
st.markdown(
    """
    #### Navigate the app using the sidebar pages:
    - **Dashboard** — full KPI overview
    - **Customer Segmentation** — value tiers, engagement, risk segments
    - **Geography Analysis** — country-level churn patterns
    - **Churn Analysis** — deep dive into churn drivers
    - **High Value Customers** — Gold/Platinum retention focus
    - **Correlation Analysis** — feature relationships & statistical patterns
    - **Prediction** — live churn prediction from a trained ML model
    - **Executive Summary** — auto-generated report for stakeholders
    """
)
