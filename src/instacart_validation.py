"""
Kiểm chứng dữ liệu Instacart Market Basket Analysis từ raw
Các nội dung:
1. Tổng quan dữ liệu, dtypes, missing values, duplicate
2. Đánh giá Target cho Regression (days_since_prior_order, basket_size), phân phối, tương quan
3. Khảo sát chuỗi thời gian: frequency, missing time, trend, seasonality, autocorrelation, data leakage, time series features
4. Baseline models và metrics đánh giá
"""
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import Ridge
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
import lightgbm as lgb
import kagglehub

print("1. Downloading / Verifying dataset via kagglehub...")
path = kagglehub.dataset_download("psparks/instacart-market-basket-analysis")
print("Path:", path)

# 1. Đọc và kiểm tra các file
files = os.listdir(path)
print("Files in dataset:", files)

# Đọc orders
orders = pd.read_csv(os.path.join(path, "orders.csv"))
print("\n--- ORDERS SHAPE & DTYPES ---")
print(f"Shape: {orders.shape}")
print(orders.dtypes)
print("\n--- MISSING VALUES ---")
print(orders.isnull().sum())
print("\n--- DUPLICATES ---")
print("Duplicate rows:", orders.duplicated().sum())
print("Duplicate order_id:", orders["order_id"].duplicated().sum())

# Đọc mẫu order_products__train để tính basket_size
op_train = pd.read_csv(os.path.join(path, "order_products__train.csv"))
print("\n--- ORDER_PRODUCTS__TRAIN SHAPE ---")
print(f"Shape: {op_train.shape}")
train_basket_size = op_train.groupby("order_id").size().rename("basket_size")

# Đọc 1 phần order_products__prior để tính basket size cho prior
print("\n--- COMPUTING BASKET SIZES FOR PRIOR ORDERS ---")
t0 = time.time()
op_prior = pd.read_csv(os.path.join(path, "order_products__prior.csv"), usecols=["order_id"])
prior_basket_size = op_prior.groupby("order_id").size().rename("basket_size")
print(f"Done computing prior basket sizes in {time.time()-t0:.2f}s")

# Merge basket_size vào orders
all_basket_sizes = pd.concat([prior_basket_size, train_basket_size])
orders["basket_size"] = orders["order_id"].map(all_basket_sizes)

print("\n--- TARGET 1: days_since_prior_order ---")
print(orders["days_since_prior_order"].describe())
print("Skewness:", orders["days_since_prior_order"].skew())
print("Censored at 30 days (%):", (orders["days_since_prior_order"] == 30).mean() * 100)

print("\n--- TARGET 2: basket_size ---")
print(orders["basket_size"].describe())
print("Skewness:", orders["basket_size"].skew())

# Correlation
corr_cols = ["order_number", "order_dow", "order_hour_of_day", "days_since_prior_order", "basket_size"]
print("\n--- CORRELATION MATRIX ---")
print(orders[corr_cols].corr())

print("\nVerification script step 1 completed successfully.")
