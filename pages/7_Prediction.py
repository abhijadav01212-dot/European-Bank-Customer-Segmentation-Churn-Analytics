import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from config.theme import CUSTOM_CSS
from utils.data_loader import load_and_prepare
from utils.machine_learning import train_models, predict_single

st.set_page_config(page_title="Prediction", page_icon=None, layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def get_data():
    return load_and_prepare("data/European_Bank.csv")


@st.cache_resource(show_spinner="Training churn prediction models…")
def get_trained_bundle(df: pd.DataFrame):
    return train_models(df)


df = get_data()
bundle = get_trained_bundle(df)

st.title("CHURN PREDICTION")
st.caption("Random Forest, Logistic Regression & Gradient Boosting trained on the current dataset")

st.markdown("### Model Performance")
metric_rows = []
for name, r in bundle["results"].items():
    metric_rows.append({
        "Model": name, "Accuracy": r["accuracy"], "Precision": r["precision"],
        "Recall": r["recall"], "F1 Score": r["f1"], "ROC AUC": r["roc_auc"],
    })
metrics_df = pd.DataFrame(metric_rows).set_index("Model").round(3)
st.dataframe(metrics_df, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    fig = go.Figure()
    for name, r in bundle["results"].items():
        fig.add_trace(go.Scatter(x=r["fpr"], y=r["tpr"], mode="lines", name=f"{name} (AUC={r['roc_auc']:.2f})"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(dash="dash", color="gray"), name="Baseline"))
    fig.update_layout(title="ROC Curves", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
                       template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#000000"), height=380)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    imp = bundle["feature_importance"].reset_index()
    imp.columns = ["Feature", "Importance"]
    fig2 = go.Figure(go.Bar(x=imp["Importance"], y=imp["Feature"], orientation="h", marker_color="#000000"))
    fig2.update_layout(title="Feature Importance (Random Forest)", template="plotly_white",
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#000000"), height=380, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Confusion Matrix")
model_choice = st.selectbox("Model", list(bundle["results"].keys()), index=1)
cm = bundle["results"][model_choice]["confusion_matrix"]
cm_fig = go.Figure(data=go.Heatmap(
    z=cm, x=["Predicted Retained", "Predicted Churned"], y=["Actual Retained", "Actual Churned"],
    text=cm, texttemplate="%{text}", colorscale="Blues",
))
cm_fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#000000"), height=350)
st.plotly_chart(cm_fig, use_container_width=True)

st.markdown("---")
st.markdown("### PREDICT CHURN FOR A NEW OR EXISTING CUSTOMER")

with st.form("predict_form"):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        geography = st.selectbox("Geography", sorted(df["Geography"].unique()))
        gender = st.selectbox("Gender", sorted(df["Gender"].unique()))
        age = st.slider("Age", 18, 92, 40)
    with fc2:
        credit_score = st.slider("Credit Score", 350, 850, 650)
        tenure = st.slider("Tenure (years)", 0, 10, 5)
        balance = st.number_input(
            "Balance (₹)", min_value=0.0, max_value=float(df["Balance_INR"].max()),
            value=float(df["Balance_INR"].median()), step=100000.0
        )
    with fc3:
        num_products = st.selectbox("Number of Products", [1, 2, 3, 4])
        salary = st.number_input(
            "Estimated Salary (₹)", min_value=0.0, max_value=float(df["EstimatedSalary_INR"].max()),
            value=float(df["EstimatedSalary_INR"].median()), step=100000.0
        )
        has_card = st.checkbox("Has Credit Card", value=True)
        is_active = st.checkbox("Is Active Member", value=True)

    model_for_pred = st.selectbox("Prediction Model", list(bundle["results"].keys()), index=1)
    submitted = st.form_submit_button("Predict Churn Risk", use_container_width=True)

if submitted:
    record = dict(
        Geography=geography, Gender=gender, Age=age, CreditScore=credit_score,
        Tenure=tenure, Balance_INR=balance, NumOfProducts=num_products,
        HasCrCard=int(has_card), IsActiveMember=int(is_active), EstimatedSalary_INR=salary,
    )
    pred, prob = predict_single(bundle, model_for_pred, record)

    if pred == 1:
        st.error(f"HIGH CHURN RISK — predicted probability: **{prob*100:.1f}%**")
    else:
        st.success(f"LIKELY TO STAY — predicted churn probability: **{prob*100:.1f}%**")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=prob * 100, number={"suffix": "%"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#4D4D4D" if pred else "#000000"},
               "steps": [{"range": [0, 40], "color": "#000000"}, {"range": [40, 70], "color": "#808080"},
                         {"range": [70, 100], "color": "#B3B3B3"}]},
        title={"text": "Predicted Churn Probability"},
    ))
    gauge.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", height=300,
                         font=dict(color="#000000"))
    st.plotly_chart(gauge, use_container_width=True)
