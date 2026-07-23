import streamlit as st
from config.theme import CUSTOM_CSS
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.charts import (
    credit_score_histogram, boxplot_by_churn, balance_salary_scatter,
    churn_by_products, tenure_line,
)
from utils.recommendations import generate_recommendations

st.set_page_config(page_title="Churn Analysis", page_icon=None, layout="wide")
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

st.title("CHURN ANALYSIS")
st.caption("Deep dive into the drivers behind customer churn")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(credit_score_histogram(df), use_container_width=True)
with c2:
    st.plotly_chart(boxplot_by_churn(df, "Age", "Age Distribution by Churn Status"), use_container_width=True)

st.plotly_chart(balance_salary_scatter(df), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(churn_by_products(df), use_container_width=True)
with c4:
    st.plotly_chart(tenure_line(df), use_container_width=True)

st.markdown("### RECOMMENDATIONS")
for rec in generate_recommendations(df):
    st.info(rec)
