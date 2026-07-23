import streamlit as st
import plotly.express as px
from config.theme import CUSTOM_CSS, CHART_SEQUENCE
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.charts import value_treemap, age_balance_bubble, boxplot_by_churn

st.set_page_config(page_title="Customer Segmentation", page_icon=None, layout="wide")
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

st.title("CUSTOMER SEGMENTATION")
st.caption("Value tiers, engagement scoring, and behavioural clusters")

c1, c2 = st.columns([3, 2])
with c1:
    st.plotly_chart(value_treemap(df), use_container_width=True)
with c2:
    value_counts = df["CustomerValue"].value_counts().reset_index()
    value_counts.columns = ["Tier", "Count"]
    fig = px.pie(value_counts, names="Tier", values="Count", hole=0.5,
                 color_discrete_sequence=CHART_SEQUENCE, title="Value Tier Split")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#000000"), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.plotly_chart(age_balance_bubble(df), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(boxplot_by_churn(df, "EngagementScore", "Engagement Score by Churn Status"), use_container_width=True)
with c4:
    risk_counts = df["ChurnRisk"].value_counts().reindex(["Low", "Medium", "High", "Very High"]).reset_index()
    risk_counts.columns = ["Risk", "Count"]
    fig2 = px.bar(risk_counts, x="Risk", y="Count", color="Risk",
                  color_discrete_sequence=["#000000", "#808080", "#666666", "#4D4D4D"],
                  title="Churn Risk Segment Distribution")
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#000000"), template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Segment Explorer")
st.dataframe(
    df.groupby(["CustomerValue", "ChurnRisk"], observed=True).agg(
        Customers=("CustomerId", "count"),
        AvgBalance=("Balance_INR", "mean"),
        ChurnRate=("Exited", "mean"),
    ).round(2).reset_index(),
    use_container_width=True,
)
