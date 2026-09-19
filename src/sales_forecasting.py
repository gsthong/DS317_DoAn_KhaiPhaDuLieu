# -*- coding: utf-8 -*-
"""
Bai toan 3: Hoi quy va du bao chuoi thoi gian
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
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import joblib
import os

sns.set_theme(style="whitegrid")
FIG = "outputs/figures"
OUT = "data/processed"
MODEL = "outputs/models"


# ---------------------------------------------------------------------------
# 3a. DU BAO DOANH THU THEO THANG (TIME SERIES)
# ---------------------------------------------------------------------------
def build_monthly_series(df):
    completed = df[df["OrderStatus"] == "Completed"]
    monthly = completed.groupby("OrderYearMonth").agg(
        Revenue=("Revenue", "sum"),
        NumOrders=("SalesOrderID", "nunique"),
    ).reset_index().sort_values("OrderYearMonth").reset_index(drop=True)
    monthly["t"] = np.arange(len(monthly))
    monthly["Month"] = pd.to_datetime(monthly["OrderYearMonth"]).dt.month
    for lag in [1, 2, 3]:
        monthly[f"Revenue_lag{lag}"] = monthly["Revenue"].shift(lag)
    monthly["RollingMean3"] = monthly["Revenue"].shift(1).rolling(3).mean()
    return monthly


def run_time_series_forecast(df):
    print(">> Xay dung chuoi doanh thu theo thang...")
    monthly = build_monthly_series(df)
    monthly_full = monthly.copy()
    monthly_model = monthly.dropna().reset_index(drop=True)
    print(f"   So thang du lieu: {len(monthly)}, dung cho huan luyen: {len(monthly_model)}")

    feature_cols = ["t", "Month", "Revenue_lag1", "Revenue_lag2", "Revenue_lag3", "RollingMean3"]
    X = monthly_model[feature_cols]
    y = monthly_model["Revenue"]

    # Chia train/test theo thoi gian (khong xao tron - dac thu chuoi thoi gian)
    split_idx = int(len(monthly_model) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=4, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, max_depth=2,
                                                         learning_rate=0.05, random_state=42),
    }

    results = []
    fitted = {}
    for name, m in models.items():
        m.fit(X_train, y_train)
        pred = m.predict(X_test)
        mae = mean_absolute_error(y_test, pred)
        rmse = np.sqrt(mean_squared_error(y_test, pred))
        mape = mean_absolute_percentage_error(y_test, pred) * 100
        r2 = r2_score(y_test, pred) if len(y_test) > 1 else np.nan
        results.append({"Model": name, "MAE": mae, "RMSE": rmse, "MAPE(%)": mape, "R2": r2})
        fitted[name] = m

    results_df = pd.DataFrame(results).sort_values("MAPE(%)")
    print(results_df)
    results_df.to_csv(f"{OUT}/forecast_model_comparison.csv", index=False)
    best_name = results_df.iloc[0]["Model"]
    best_model = fitted[best_name]
    print(f">> Mo hinh du bao tot nhat: {best_name}")

    # Du bao toan bo chuoi (fitted) de ve bieu do so sanh thuc te vs du doan
    monthly_model["Predicted"] = best_model.predict(X)

    plt.figure(figsize=(13, 5.5))
    plt.plot(monthly_full["OrderYearMonth"], monthly_full["Revenue"], marker="o",
             label="Doanh thu thuc te", color="#1f77b4", linewidth=2)
    plt.plot(monthly_model["OrderYearMonth"], monthly_model["Predicted"], marker="x",
             linestyle="--", label=f"Du bao ({best_name})", color="#d62728", linewidth=2)
    plt.axvline(monthly_model["OrderYearMonth"].iloc[split_idx], color="gray", linestyle=":", label="Diem chia Train/Test")
    plt.xticks(rotation=75, fontsize=8)
    plt.ylabel("Doanh thu")
    plt.title("Du bao doanh thu theo thang: Thuc te vs Mo hinh")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{FIG}/24_revenue_forecast_actual_vs_predicted.png", bbox_inches="tight")
    plt.close()

    # Du bao 3 thang tiep theo (out-of-sample, ngoai du lieu quan sat)
    last_rows = monthly_full.tail(3)["Revenue"].tolist()
    future_preds = []
    hist = monthly_full["Revenue"].tolist()
    t_next = monthly_full["t"].max() + 1
    last_month = monthly_full["Month"].iloc[-1]
    for i in range(3):
        next_month = (last_month % 12) + 1
        lag1, lag2, lag3 = hist[-1], hist[-2], hist[-3]
        roll3 = np.mean(hist[-3:])
        x_next = pd.DataFrame([{
            "t": t_next, "Month": next_month, "Revenue_lag1": lag1,
            "Revenue_lag2": lag2, "Revenue_lag3": lag3, "RollingMean3": roll3,
        }])[feature_cols]
        pred_next = best_model.predict(x_next)[0]
        future_preds.append(pred_next)
        hist.append(pred_next)
        t_next += 1
        last_month = next_month

    print(">> Du bao doanh thu 3 thang tiep theo:", [round(p, 0) for p in future_preds])

    fig, ax = plt.subplots(figsize=(9, 2))
    ax.axis("off")
    fdf = pd.DataFrame({"Thang du bao": ["T+1", "T+2", "T+3"],
                         "DoanhThuDuBao": [f"{p:,.0f}" for p in future_preds]})
    tbl = ax.table(cellText=fdf.values, colLabels=fdf.columns, cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1, 2)
    plt.title(f"Du bao doanh thu 3 thang tiep theo ({best_name})", pad=15)
    plt.tight_layout()
    plt.savefig(f"{FIG}/25_revenue_forecast_next3months.png", bbox_inches="tight", dpi=130)
    plt.close()

    joblib.dump(best_model, f"{MODEL}/revenue_forecast_model.pkl")
    return results_df, future_preds


# ---------------------------------------------------------------------------
# 3b. HOI QUY DU DOAN GIA TRI DON HANG
# ---------------------------------------------------------------------------
def run_order_value_regression(df):
    print(">> Chuan bi du lieu hoi quy gia tri dong hang...")
    completed = df[df["OrderStatus"] == "Completed"].copy()

    feats = completed[[
        "Quantity", "DiscountPct", "HasPromotion", "CategoryName", "BrandName",
        "ChannelName", "FulfillmentMethod", "AgeBand", "GovernorateName",
        "OrderMonth", "Revenue",
    ]].dropna(subset=["Revenue", "Quantity"])

    # Loai outlier cuc doan de mo hinh on dinh hon
    q_low, q_high = feats["Revenue"].quantile([0.01, 0.99])
    feats = feats[(feats["Revenue"] >= q_low) & (feats["Revenue"] <= q_high)]

    y = feats["Revenue"]
    X = feats.drop(columns=["Revenue"])
    num_cols = ["Quantity", "DiscountPct"]
    cat_cols = ["HasPromotion", "CategoryName", "BrandName", "ChannelName",
                "FulfillmentMethod", "AgeBand", "GovernorateName", "OrderMonth"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ], sparse_threshold=0)  # xuat dense array - Random Forest xu ly dense nhanh hon nhieu so voi sparse

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=80, max_depth=8, min_samples_leaf=30,
                                                random_state=42, n_jobs=-1),
        "Hist Gradient Boosting": HistGradientBoostingRegressor(max_iter=150, max_depth=6, random_state=42),
    }

    results = []
    fitted = {}
    for name, m in models.items():
        pipe = Pipeline([("prep", preprocessor), ("reg", m)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        results.append({
            "Model": name,
            "MAE": mean_absolute_error(y_test, pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, pred)),
            "R2": r2_score(y_test, pred),
        })
        fitted[name] = pipe

    results_df = pd.DataFrame(results).sort_values("R2", ascending=False)
    print(results_df)
    results_df.to_csv(f"{OUT}/order_value_regression_comparison.csv", index=False)
    best_name = results_df.iloc[0]["Model"]
    best_pipe = fitted[best_name]

    y_pred_best = best_pipe.predict(X_test)
    plt.figure(figsize=(7, 7))
    plt.scatter(y_test, y_pred_best, alpha=0.15, s=8, color="#1f77b4")
    lims = [min(y_test.min(), y_pred_best.min()), max(y_test.max(), y_pred_best.max())]
    plt.plot(lims, lims, "r--", linewidth=1.5, label="Du doan hoan hao")
    plt.xlabel("Gia tri thuc te")
    plt.ylabel("Gia tri du doan")
    plt.title(f"Hoi quy gia tri dong hang: Thuc te vs Du doan ({best_name})")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{FIG}/26_order_value_regression_scatter.png", bbox_inches="tight")
    plt.close()

    joblib.dump(best_pipe, f"{MODEL}/order_value_regression_model.pkl")
    return results_df


if __name__ == "__main__":
    df = pd.read_parquet(f"{OUT}/sales_fact.parquet")
    run_time_series_forecast(df)
    run_order_value_regression(df)
