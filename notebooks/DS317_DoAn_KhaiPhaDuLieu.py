# %% [markdown]
# # Đồ án môn học: Khai phá dữ liệu trong doanh nghiệp (DS317)
#
# **Dataset:** Electronics Sales Dataset (B.Tech style)

# %% [markdown]
# ## 0. Thiết lập môi trường

# %%
import sys, os
os.chdir("..")  # dam bao working directory la project/
sys.path.insert(0, "src")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Image

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 140)

import preprocessing, eda, customer_segmentation, return_prediction, sales_forecasting, market_basket

print("Da nap tat ca cac module xu ly.")

# %% [markdown]
# ## 1. Tổng quan dữ liệu gốc (26 bảng)

# %%
dfs, dedup_stats = preprocessing.load_raw()
dq = preprocessing.data_quality_report(dfs)
display(dq)
print("So dong trung lap da duoc khu trong buoc doc du lieu:", dedup_stats)

# %%
miss = preprocessing.missing_by_column(dfs)
display(miss[miss["TyLeThieu(%)"] > 20])

# %% [markdown]
# ## 2. Tiền xử lý và tích hợp dữ liệu

# %%
dim_sku = preprocessing.build_dim_product(dfs)
dim_cust = preprocessing.build_dim_customer(dfs)
fact_raw = preprocessing.build_sales_fact(dfs, dim_sku, dim_cust)
fact, clean_stats = preprocessing.clean_sales_fact(fact_raw)
display(pd.DataFrame([clean_stats]))
print("Kich thuoc bang fact sau xu ly:", fact.shape)
fact.head(3)

# %% [markdown]
# ## 3. Khám phá dữ liệu (EDA)

# %%
summary = eda.run_eda(fact)
display(pd.DataFrame([summary]).T.rename(columns={0: "Gia tri"}))

# %% [markdown]
# ### 3.1 Trạng thái đơn hàng & xu hướng doanh thu

# %%
display(Image("outputs/figures/01_order_status_pie.png"))
display(Image("outputs/figures/02_monthly_revenue_trend.png"))

# %% [markdown]
# ### 3.2 Doanh thu theo ngành hàng, thương hiệu, kênh bán

# %%
display(Image("outputs/figures/03_revenue_by_category.png"))
display(Image("outputs/figures/04_top_brands_revenue.png"))
display(Image("outputs/figures/05_revenue_by_channel.png"))

# %% [markdown]
# ### 3.3 Đặc điểm khách hàng & khu vực địa lý

# %%
display(Image("outputs/figures/06_customer_age_distribution.png"))
display(Image("outputs/figures/07_revenue_by_governorate.png"))

# %% [markdown]
# ### 3.4 Phân phối giá & tương quan các biến số

# %%
display(Image("outputs/figures/08_price_distribution.png"))
display(Image("outputs/figures/12_correlation_matrix.png"))

# %% [markdown]
# ### 3.5 Phân tích trả hàng (Returns)

# %%
display(Image("outputs/figures/09_return_rate_by_category.png"))
display(Image("outputs/figures/10_return_reasons.png"))

# %% [markdown]
# ### 3.6 Các phân tích khác

# %%
display(Image("outputs/figures/11_heatmap_month_category.png"))
display(Image("outputs/figures/13_revenue_by_fulfillment.png"))
display(Image("outputs/figures/14_price_boxplot_by_category.png"))
display(Image("outputs/figures/15_orders_by_dayofweek.png"))

# %% [markdown]
# ## 4. Bài toán 1 - Phân cụm: Phân khúc khách hàng (RFM + K-Means)

# %%
rfm, profile, sil = customer_segmentation.run_segmentation(fact)
display(Image("outputs/figures/16_kmeans_elbow_silhouette.png"))

# %%
display(Image("outputs/figures/17_customer_segments_pca.png"))
display(Image("outputs/figures/18_segment_customer_count.png"))
display(Image("outputs/figures/19_segment_profile_table.png"))
display(profile)

# %% [markdown]
# ## 5. Bài toán 2 - Phân loại: Dự đoán khả năng trả hàng

# %%
clf_results, best_clf = return_prediction.run_classification(fact)
display(clf_results)
display(Image("outputs/figures/20_classification_roc_curves.png"))
display(Image("outputs/figures/21_confusion_matrix_best_model.png"))
display(Image("outputs/figures/23_feature_importance.png"))

# %% [markdown]
# ## 6. Bài toán 3 - Hồi quy & Chuỗi thời gian: Dự báo doanh thu
#
# ### 6.1 Dự báo doanh thu theo tháng (Time Series)

# %%
ts_results, future_preds = sales_forecasting.run_time_series_forecast(fact)
display(ts_results)
display(Image("outputs/figures/24_revenue_forecast_actual_vs_predicted.png"))
display(Image("outputs/figures/25_revenue_forecast_next3months.png"))

# %% [markdown]
# ### 6.2 Hồi quy giá trị dòng hàng (Order Value Regression)

# %%
reg_results = sales_forecasting.run_order_value_regression(fact)
display(reg_results)
display(Image("outputs/figures/26_order_value_regression_scatter.png"))

# %% [markdown]
# ## 7. Bài toán 4 - Luật kết hợp: Phân tích giỏ hàng (Apriori)

# %%
freq_items, rules = market_basket.run_market_basket(fact)
display(rules.head(15))
display(Image("outputs/figures/27_association_rules_top_lift.png"))
display(Image("outputs/figures/28_association_rules_scatter.png"))

# %% [markdown]
# ## 8. Tổng kết
#
# | Bài toán | Kỹ thuật | Kết quả chính |
# |---|---|---|
# | Phân khúc khách hàng | K-Means (RFM) | 3 cụm, Silhouette ≈ 0.40 |
# | Dự đoán trả hàng | Random Forest / GBM | AUC ≈ 0.55 |
# | Dự báo doanh thu tháng | Random Forest (lag features) | MAPE ≈ 9.1% |
# | Hồi quy giá trị đơn hàng | Hist Gradient Boosting | R² ≈ 0.77 |
# | Luật kết hợp giỏ hàng | Apriori | 168 luật (lift cao nhất ≈ 17.0) |
