"""Churn prediction models: training, evaluation, and single-record inference."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix,
)

FEATURES = [
    "CreditScore", "Age", "Tenure", "Balance_INR", "NumOfProducts",
    "HasCrCard", "IsActiveMember", "EstimatedSalary_INR", "Geography_enc", "Gender_enc",
]


def prepare_ml_frame(df: pd.DataFrame):
    d = df.copy()
    geo_enc = LabelEncoder().fit(d["Geography"])
    gender_enc = LabelEncoder().fit(d["Gender"])
    d["Geography_enc"] = geo_enc.transform(d["Geography"])
    d["Gender_enc"] = gender_enc.transform(d["Gender"])
    X = d[FEATURES]
    y = d["Exited"]
    return X, y, geo_enc, gender_enc


def train_models(df: pd.DataFrame, random_state: int = 42) -> dict:
    """Train Logistic Regression, Random Forest, and Gradient Boosting.
    Returns a dict with fitted models, scaler, encoders, test data & metrics.
    """
    X, y, geo_enc, gender_enc = prepare_ml_frame(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    scaler = StandardScaler().fit(X_train)
    X_train_s = scaler.transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=250, max_depth=10, random_state=random_state),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=random_state),
    }

    results = {}
    for name, model in models.items():
        if name == "Logistic Regression":
            model.fit(X_train_s, y_train)
            preds = model.predict(X_test_s)
            probs = model.predict_proba(X_test_s)[:, 1]
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1]

        fpr, tpr, _ = roc_curve(y_test, probs)
        results[name] = {
            "model": model,
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "f1": f1_score(y_test, preds, zero_division=0),
            "roc_auc": roc_auc_score(y_test, probs),
            "confusion_matrix": confusion_matrix(y_test, preds),
            "fpr": fpr, "tpr": tpr,
        }

    # feature importance from Random Forest (most interpretable of the tree models)
    importance = pd.Series(
        results["Random Forest"]["model"].feature_importances_, index=FEATURES
    ).sort_values(ascending=False)

    return {
        "results": results,
        "scaler": scaler,
        "geo_enc": geo_enc,
        "gender_enc": gender_enc,
        "feature_importance": importance,
        "X_test": X_test, "y_test": y_test,
    }


def predict_single(bundle: dict, model_name: str, record: dict) -> tuple[int, float]:
    """Predict churn (0/1) and probability for a single customer input dict."""
    geo_enc = bundle["geo_enc"]
    gender_enc = bundle["gender_enc"]
    row = pd.DataFrame([{
        "CreditScore": record["CreditScore"],
        "Age": record["Age"],
        "Tenure": record["Tenure"],
        "Balance_INR": record["Balance_INR"],
        "NumOfProducts": record["NumOfProducts"],
        "HasCrCard": record["HasCrCard"],
        "IsActiveMember": record["IsActiveMember"],
        "EstimatedSalary_INR": record["EstimatedSalary_INR"],
        "Geography_enc": geo_enc.transform([record["Geography"]])[0],
        "Gender_enc": gender_enc.transform([record["Gender"]])[0],
    }])[FEATURES]

    model = bundle["results"][model_name]["model"]
    if model_name == "Logistic Regression":
        row_in = bundle["scaler"].transform(row)
    else:
        row_in = row
    pred = int(model.predict(row_in)[0])
    prob = float(model.predict_proba(row_in)[0, 1])
    return pred, prob
