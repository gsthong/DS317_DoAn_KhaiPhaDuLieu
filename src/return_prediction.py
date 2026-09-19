# -*- coding: utf-8 -*-
"""
Bai toan 2: Du doan kha nang tra hang (Return Prediction)
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score,
                              roc_curve, precision_recall_curve, f1_score)
import joblib
import os

sns.set_theme(style="whitegrid")
FIG = "outputs/figures"
OUT = "data/processed"
MODEL = "outputs/models"


def build_feature_set(df):
    """Trich xuat dac trung tai thoi diem dat hang de tranh ro ri du lieu (data leakage)."""
    d = df[df["OrderStatus"] == "Completed"].copy()

    feats = d[[
        "Quantity", "ActualSellingPrice", "DiscountPct", "HasPromotion",
        "CategoryName", "BrandName", "ChannelName", "FulfillmentMethod",
        "AgeBand", "GovernorateName", "OrderMonth", "OrderDayOfWeek",
        "IsReturned",
    ]].copy()

    feats = feats.dropna(subset=["ActualSellingPrice", "Quantity"])
    return feats


def run_classification(df):
    print(">> Chuan bi du lieu cho bai toan phan loai...")
    feats = build_feature_set(df)
    print("   Kich thuoc du lieu:", feats.shape)
    print("   Ty le lop duong (tra hang):", feats["IsReturned"].mean())

    y = feats["IsReturned"].astype(int)
    X = feats.drop(columns=["IsReturned"])

    num_cols = ["Quantity", "ActualSellingPrice", "DiscountPct"]
    cat_cols = ["HasPromotion", "CategoryName", "BrandName", "ChannelName",
                "FulfillmentMethod", "AgeBand", "GovernorateName", "OrderMonth", "OrderDayOfWeek"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y)
    print(f"   Train: {X_train.shape}, Test: {X_test.shape}")

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=True), cat_cols),
    ])

    models = {
        "Logistic Regression": LogisticRegression(max_iter=500, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_leaf=20,
            class_weight="balanced", random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=3, learning_rate=0.1, random_state=42),
    }

    results = []
    fitted = {}
    plt.figure(figsize=(7, 6))
    for name, clf in models.items():
        pipe = Pipeline([("prep", preprocessor), ("clf", clf)])
        print(f">> Huan luyen {name}...")
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_proba = pipe.predict_proba(X_test)[:, 1]

        auc = roc_auc_score(y_test, y_proba)
        f1 = f1_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)

        results.append({
            "Model": name, "AUC": auc, "F1": f1,
            "Precision": report["1"]["precision"], "Recall": report["1"]["recall"],
            "Accuracy": report["accuracy"],
        })
        fitted[name] = pipe

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})", linewidth=2)

    plt.plot([0, 1], [0, 1], "k--", alpha=0.4, label="Random baseline")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Duong cong ROC - So sanh cac mo hinh phan loai tra hang")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{FIG}/20_classification_roc_curves.png", bbox_inches="tight")
    plt.close()

    results_df = pd.DataFrame(results).sort_values("AUC", ascending=False)
    print(results_df)
    results_df.to_csv(f"{OUT}/classification_model_comparison.csv", index=False)

    best_name = results_df.iloc[0]["Model"]
    best_pipe = fitted[best_name]
    print(f">> Mo hinh tot nhat: {best_name}")

    # Confusion matrix cua mo hinh tot nhat
    y_pred_best = best_pipe.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Khong tra", "Co tra hang"],
                yticklabels=["Khong tra", "Co tra hang"])
    plt.title(f"Ma tran nham lan - {best_name}")
    plt.ylabel("Thuc te")
    plt.xlabel("Du doan")
    plt.tight_layout()
    plt.savefig(f"{FIG}/21_confusion_matrix_best_model.png", bbox_inches="tight")
    plt.close()

    # Bang so sanh mo hinh (hinh anh)
    fig, ax = plt.subplots(figsize=(9, 2.2))
    ax.axis("off")
    disp = results_df.round(4)
    tbl = ax.table(cellText=disp.values, colLabels=disp.columns, cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 1.8)
    plt.title("So sanh hieu nang cac mo hinh phan loai du doan tra hang", pad=15)
    plt.tight_layout()
    plt.savefig(f"{FIG}/22_classification_model_comparison_table.png", bbox_inches="tight", dpi=130)
    plt.close()

    # Feature importance (neu la tree-based model)
    if best_name in ["Random Forest", "Gradient Boosting"]:
        ohe = best_pipe.named_steps["prep"].named_transformers_["cat"]
        cat_feature_names = ohe.get_feature_names_out(cat_cols)
        all_feature_names = num_cols + list(cat_feature_names)
        importances = best_pipe.named_steps["clf"].feature_importances_
        imp_df = pd.DataFrame({"Feature": all_feature_names, "Importance": importances})
        imp_df = imp_df.sort_values("Importance", ascending=False).head(15)

        plt.figure(figsize=(9, 7))
        sns.barplot(data=imp_df, x="Importance", y="Feature", hue="Feature", palette="mako", legend=False)
        plt.title(f"Top 15 dac trung quan trong nhat - {best_name}")
        plt.tight_layout()
        plt.savefig(f"{FIG}/23_feature_importance.png", bbox_inches="tight")
        plt.close()

    joblib.dump(best_pipe, f"{MODEL}/return_prediction_model.pkl")
    return results_df, best_pipe


if __name__ == "__main__":
    df = pd.read_parquet(f"{OUT}/sales_fact.parquet")
    run_classification(df)
