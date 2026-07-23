import streamlit as st
import plotly.express as px
from config.theme import CUSTOM_CSS, GEO_COLORS
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.charts import churn_by_geography, revenue_at_risk_waterfall

st.set_page_config(page_title="Geography Analysis", page_icon=None, layout="wide")
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

st.title("GEOGRAPHY ANALYSIS")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(churn_by_geography(df), use_container_width=True)
with c2:
    counts = df["Geography"].value_counts().reset_index()
    counts.columns = ["Geography", "Customers"]
    fig = px.bar(counts, x="Geography", y="Customers", color="Geography",
                 color_discrete_map=GEO_COLORS, text_auto=True, title="Customer Volume by Country")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#000000"), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.plotly_chart(revenue_at_risk_waterfall(df), use_container_width=True)

st.markdown("### Country Summary Table")
summary = df.groupby("Geography").agg(
    Customers=("CustomerId", "count"),
    ChurnRate=("Exited", "mean"),
    AvgBalance=("Balance_INR", "mean"),
    AvgSalary=("EstimatedSalary_INR", "mean"),
    AvgCreditScore=("CreditScore", "mean"),
    RevenueAtRisk=("RevenueRisk", "sum"),
).round(2)
summary["ChurnRate"] = (summary["ChurnRate"] * 100).round(1).astype(str) + "%"
st.dataframe(summary, use_container_width=True)
