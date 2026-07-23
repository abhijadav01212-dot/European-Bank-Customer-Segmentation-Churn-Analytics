import streamlit as st
from config.theme import CUSTOM_CSS
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.kpi_cards import compute_kpis, render_kpi_row
from utils.charts import (
    churn_by_geography, churn_by_age_group, churn_by_products,
    gender_churn_grouped, tenure_line, active_member_sunburst,
)

st.set_page_config(page_title="Dashboard", page_icon=None, layout="wide")
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

st.title("EXECUTIVE DASHBOARD")

kpis = compute_kpis(df)
render_kpi_row(kpis, ["Total Customers", "Churn Rate", "Retention Rate", "Exited Customers"])
st.write("")
render_kpi_row(kpis, ["Avg Salary", "Avg Tenure", "Inactive Members", "High Value Customers"])
st.write("")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(churn_by_geography(df), use_container_width=True)
with c2:
    st.plotly_chart(churn_by_age_group(df), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(churn_by_products(df), use_container_width=True)
with c4:
    st.plotly_chart(gender_churn_grouped(df), use_container_width=True)

c5, c6 = st.columns(2)
with c5:
    st.plotly_chart(tenure_line(df), use_container_width=True)
with c6:
    st.plotly_chart(active_member_sunburst(df), use_container_width=True)

st.dataframe(df.head(200), use_container_width=True, height=300)
