import streamlit as st
from config.theme import CUSTOM_CSS
from utils.data_loader import load_and_prepare, apply_filters
from utils.sidebar import render_sidebar_filters
from utils.charts import correlation_heatmap

st.set_page_config(page_title="Correlation Analysis", page_icon=None, layout="wide")
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

st.title("CORRELATION ANALYSIS")
st.caption("Statistical relationships between numeric features and churn")

st.plotly_chart(correlation_heatmap(df), use_container_width=True)

st.markdown("### How to Read This")
st.markdown(
    """
    - Values close to **+1** mean two features rise together.
    - Values close to **-1** mean one rises as the other falls.
    - Look at the **Exited** row/column for the strongest churn drivers in the current filter.
    """
)

corr_with_exit = df[["CreditScore", "Age", "Tenure", "Balance_INR", "NumOfProducts",
                      "HasCrCard", "IsActiveMember", "EstimatedSalary_INR", "Exited"]].corr()["Exited"].drop("Exited").sort_values(key=abs, ascending=False)
st.markdown("### Strongest Correlations with Churn")
st.dataframe(corr_with_exit.round(3).rename("Correlation with Exited").reset_index().rename(columns={"index": "Feature"}),
             use_container_width=True)
