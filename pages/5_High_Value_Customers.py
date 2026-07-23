import streamlit as st
import plotly.express as px
from config.theme import CUSTOM_CSS
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.kpi_cards import render_kpi_row

st.set_page_config(page_title="High Value Customers", page_icon=None, layout="wide")
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

st.title("HIGH VALUE CUSTOMERS")
st.caption("Gold & Platinum tier customers — the highest-priority retention segment")

hv = df[df["CustomerValue"].isin(["Gold", "Platinum"])]

kpis = {
    "High Value Customers": f"{len(hv):,}",
    "% of Base": f"{(len(hv)/len(df)*100 if len(df) else 0):.1f}%",
    "HV Churn Rate": f"{(hv['Exited'].mean()*100 if len(hv) else 0):.1f}%",
    "HV Revenue at Risk": f"₹{hv['RevenueRisk'].sum():,.0f}",
}
render_kpi_row(kpis, list(kpis.keys()))
st.write("")

c1, c2 = st.columns(2)
with c1:
    fig = px.histogram(hv, x="Balance_INR", color="Exited", nbins=30, barmode="overlay",
                        color_discrete_map={0: "#000000", 1: "#4D4D4D"},
                        title="High-Value Customer Balance Distribution")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#000000"), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    geo_hv = hv.groupby("Geography").size().reset_index(name="Count")
    fig2 = px.bar(geo_hv, x="Geography", y="Count", title="High-Value Customers by Country",
                  color="Geography", color_discrete_sequence=["#000000", "#4D4D4D", "#808080"])
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#000000"), template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### AT-RISK HIGH-VALUE CUSTOMERS (PRIORITY OUTREACH LIST)")
at_risk = hv[hv["ChurnRisk"].isin(["High", "Very High"])].sort_values("Balance_INR", ascending=False)
st.dataframe(
    at_risk[["CustomerId", "Geography", "Gender", "Age", "Balance_INR", "CustomerValue", "ChurnRisk", "EngagementScore"]].head(100),
    use_container_width=True, height=400,
)
