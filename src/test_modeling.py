"""
Test feature engineering and baseline model evaluation
"""
import os
import time
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
import lightgbm as lgb
import kagglehub

path = kagglehub.dataset_download("psparks/instacart-market-basket-analysis")
orders = pd.read_csv(os.path.join(path, "orders.csv"))

# Lấy 30,000 users để test nhanh
train_users = orders[orders["eval_set"] == "train"]["user_id"].unique()
np.random.seed(42)
sampled_users = np.random.choice(train_users, size=30000, replace=False)
orders_sample = orders[orders["user_id"].isin(sampled_users)].copy()
orders_sample.sort_values(["user_id", "order_number"], inplace=True)

print(f"Sampled {len(sampled_users)} users, {len(orders_sample)} orders.")

# Tạo lag features trong group
orders_sample["lag_1_days"] = orders_sample.groupby("user_id")["days_since_prior_order"].shift(1)
orders_sample["lag_2_days"] = orders_sample.groupby("user_id")["days_since_prior_order"].shift(2)
orders_sample["lag_3_days"] = orders_sample.groupby("user_id")["days_since_prior_order"].shift(3)

# Rolling stats (expanding mean của các đơn trước, tránh leakage)
orders_sample["user_cum_mean_days"] = (
    orders_sample.groupby("user_id")["days_since_prior_order"]
    .apply(lambda x: x.shift(1).expanding().mean())
    .reset_index(level=0, drop=True)
)

orders_sample["user_cum_std_days"] = (
    orders_sample.groupby("user_id")["days_since_prior_order"]
    .apply(lambda x: x.shift(1).expanding().std())
    .reset_index(level=0, drop=True)
).fillna(0)

# Cyclical features
orders_sample["sin_hour"] = np.sin(2 * np.pi * orders_sample["order_hour_of_day"] / 24.0)
orders_sample["cos_hour"] = np.cos(2 * np.pi * orders_sample["order_hour_of_day"] / 24.0)
orders_sample["sin_dow"] = np.sin(2 * np.pi * orders_sample["order_dow"] / 7.0)
orders_sample["cos_dow"] = np.cos(2 * np.pi * orders_sample["order_dow"] / 7.0)
orders_sample["is_weekend"] = (orders_sample["order_dow"] <= 1).astype(int)

# Target: days_since_prior_order
# Train: Đơn hàng áp chót (order_number = max - 1)
# Test: Đơn hàng cuối cùng (eval_set == 'train')
test_df = orders_sample[orders_sample["eval_set"] == "train"].copy()

# Lấy đơn hàng áp chót cho train
max_order_num = orders_sample.groupby("user_id")["order_number"].transform("max")
train_df = orders_sample[(orders_sample["order_number"] == max_order_num - 1) & (orders_sample["order_number"] >= 4)].copy()

features = [
    "order_number", "order_dow", "order_hour_of_day",
    "sin_hour", "cos_hour", "sin_dow", "cos_dow", "is_weekend",
    "lag_1_days", "lag_2_days", "lag_3_days",
    "user_cum_mean_days", "user_cum_std_days"
]

target = "days_since_prior_order"

X_train = train_df[features].fillna(train_df[features].median())
y_train = train_df[target]

X_test = test_df[features].fillna(train_df[features].median())
y_test = test_df[target]

print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")

# Model 0: Dummy Mean
dummy = DummyRegressor(strategy="mean")
dummy.fit(X_train, y_train)
y_pred_dummy = dummy.predict(X_test)

# Model 1: Naive Last Value (Persistence lag_1_days)
y_pred_naive = X_test["lag_1_days"]

# Model 2: Ridge
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)
y_pred_ridge = ridge.predict(X_test)

# Model 3: LightGBM
lgb_model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.05, random_state=42, verbose=-1)
lgb_model.fit(X_train, y_train)
y_pred_lgb = lgb_model.predict(X_test)

def evaluate(y_true, y_pred, name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    medae = median_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    # MAPE (tránh chia 0 bằng cách + 1)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-5))) * 100
    print(f"[{name}] MAE: {mae:.4f} | RMSE: {rmse:.4f} | MedAE: {medae:.4f} | R2: {r2:.4f}")
    return {"Model": name, "MAE": mae, "RMSE": rmse, "MedAE": medae, "R2": r2}

print("\n--- EVALUATION RESULTS ---")
evaluate(y_test, y_pred_dummy, "Baseline 0: Mean Predictor")
evaluate(y_test, y_pred_naive, "Baseline 1: Persistence (Lag-1)")
evaluate(y_test, y_pred_ridge, "Baseline 2: Ridge Regression")
evaluate(y_test, y_pred_lgb, "Baseline 3: LightGBM Regressor")
