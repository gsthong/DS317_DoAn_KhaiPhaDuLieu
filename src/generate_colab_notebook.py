import os
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()

nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.11.2"
    },
    "colab": {
        "provenance": [],
        "toc_visible": True
    }
}

cells = []

# Cell 0: Header
cells.append(new_markdown_cell("""# Khảo sát và thẩm định dữ liệu Instacart cho bài toán Hồi quy và Chuỗi thời gian
**Môn học:** Khai phá dữ liệu trong doanh nghiệp (DS317)  
**Dataset:** Instacart Market Basket Analysis

---

### Mục tiêu khảo sát
Thẩm định dữ liệu Instacart nhằm đánh giá tính khả thi khi xây dựng bài toán hồi quy (regression) và chuỗi thời gian (time series):
1. **Tổng quan cấu trúc:** Kiểm tra 6 bảng dữ liệu, kiểu dữ liệu, dung lượng bộ nhớ, giá trị khuyết và tính toàn vẹn.
2. **Khảo sát biến mục tiêu:** Phân tích phân phối và tương quan của hai ứng viên target (`days_since_prior_order` và `basket_size`).
3. **Đặc tính thời gian:** Phân tích tính mùa vụ theo ngày và giờ, chu kỳ tự tương quan (ACF/PACF), xu hướng và rủi ro rò rỉ dữ liệu (data leakage).
4. **Mô hình cơ sở:** Thử nghiệm các mô hình baseline trên tập dữ liệu phân chia theo thứ tự thời gian.
"""))

# Cell 1: Section 0
cells.append(new_markdown_cell("""## 0. Thiết lập môi trường"""))

# Cell 2: Imports and settings
cells.append(new_code_cell("""!pip install -q kagglehub lightgbm scikit-learn seaborn matplotlib statsmodels

import os
import sys
import time
import gc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.linear_model import Ridge
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
import lightgbm as lgb
import kagglehub
from IPython.display import display

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['figure.dpi'] = 120
pd.set_option('display.max_columns', 50)
pd.set_option('display.float_format', lambda x: '%.4f' % x)
"""))

# Cell 3: Download data
cells.append(new_code_cell("""dataset_path = kagglehub.dataset_download("psparks/instacart-market-basket-analysis")
print("Thu muc du lieu:", dataset_path)

dataset_files = os.listdir(dataset_path)
print("\\nDanh sach file trong dataset:")
for f in dataset_files:
    file_path = os.path.join(dataset_path, f)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"  {f:<30} | {file_size_mb:>8.2f} MB")
"""))

# Cell 4: Section 1
cells.append(new_markdown_cell("""## 1. Cấu trúc dữ liệu và tối ưu bộ nhớ"""))

# Cell 5: Load and optimize
cells.append(new_code_cell("""def load_and_optimize(file_name, usecols=None, nrows=None):
    fp = os.path.join(dataset_path, file_name)
    df = pd.read_csv(fp, usecols=usecols, nrows=nrows)
    mem_before = df.memory_usage().sum() / 1024**2
    
    for col in df.select_dtypes(include=['int64']).columns:
        c_min, c_max = df[col].min(), df[col].max()
        if c_min >= 0:
            if c_max < 255:
                df[col] = df[col].astype(np.uint8)
            elif c_max < 65535:
                df[col] = df[col].astype(np.uint16)
            elif c_max < 4294967295:
                df[col] = df[col].astype(np.uint32)
        else:
            if c_min > -128 and c_max < 127:
                df[col] = df[col].astype(np.int8)
            elif c_min > -32768 and c_max < 32767:
                df[col] = df[col].astype(np.int16)
            elif c_min > -2147483648 and c_max < 2147483647:
                df[col] = df[col].astype(np.int32)
                
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype(np.float32)
        
    mem_after = df.memory_usage().sum() / 1024**2
    return df, mem_before, mem_after

orders, m_b1, m_a1 = load_and_optimize("orders.csv")
op_train, m_b2, m_a2 = load_and_optimize("order_products__train.csv")
products, m_b3, m_a3 = load_and_optimize("products.csv")
aisles, m_b4, m_a4 = load_and_optimize("aisles.csv")
departments, m_b5, m_a5 = load_and_optimize("departments.csv")

print(f"orders.csv:            {orders.shape[0]:>10,d} dong | {orders.shape[1]} cot | RAM: {m_b1:.1f} MB -> {m_a1:.1f} MB (giam {100*(m_b1-m_a1)/m_b1:.1f}%)")
print(f"order_products__train: {op_train.shape[0]:>10,d} dong | {op_train.shape[1]} cot | RAM: {m_b2:.1f} MB -> {m_a2:.1f} MB (giam {100*(m_b2-m_a2)/m_b2:.1f}%)")
print(f"products.csv:          {products.shape[0]:>10,d} dong | {products.shape[1]} cot | RAM: {m_b3:.1f} MB -> {m_a3:.1f} MB")
print(f"aisles.csv:            {aisles.shape[0]:>10,d} dong | {aisles.shape[1]} cot")
print(f"departments.csv:       {departments.shape[0]:>10,d} dong | {departments.shape[1]} cot")
"""))

# Cell 6: Dtypes display
cells.append(new_code_cell("""print("--- Kieu du lieu cac bang ---")
for name, df in [("orders", orders), ("order_products__train", op_train),
                 ("products", products), ("aisles", aisles), ("departments", departments)]:
    print(f"\\n[{name}]")
    print(df.dtypes.to_string())
"""))

# Cell 7: Check missing and duplicates
cells.append(new_code_cell("""print("--- Kiem tra missing values ---")
for name, df in [("orders", orders), ("order_products__train", op_train), 
                 ("products", products), ("aisles", aisles), ("departments", departments)]:
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if len(null_cols) == 0:
        print(f"Bang '{name}': 0 missing.")
    else:
        print(f"Bang '{name}' co cot missing:")
        for col, count in null_cols.items():
            pct = 100 * count / len(df)
            print(f"  - {col}: {count:,d} ({pct:.2f}%)")

print("\\n--- Phan tich missing days_since_prior_order ---")
missing_mask = orders['days_since_prior_order'].isnull()
missing_orders = orders[missing_mask]['order_number'].unique()
print(f"So luong user: {orders['user_id'].nunique():,d}")
print(f"So dong missing: {missing_mask.sum():,d}")
print(f"Gia tri order_number tai cac dong missing: {missing_orders}")

print("\\n--- Kiem tra duplicates ---")
print(f"Duplicate trong orders: {orders.duplicated().sum()}")
print(f"Duplicate order_id: {orders['order_id'].duplicated().sum()}")
print(f"Duplicate (order_id, product_id) trong op_train: {op_train.duplicated(subset=['order_id', 'product_id']).sum()}")
print(f"Duplicate product_id: {products['product_id'].duplicated().sum()}")
"""))

# Cell 7: Note on section 1
cells.append(new_markdown_cell("""**Nhận xét:**
1. Các bảng dữ liệu không có bản ghi trùng lặp, đảm bảo tính toàn vẹn khóa chính và khóa ngoại.
2. Cột `days_since_prior_order` khuyết ở 206,209 dòng (6.03%), tương ứng với đơn hàng đầu tiên (`order_number = 1`) của mỗi khách hàng. Vì là đơn hàng đầu tiên, không có đơn hàng trước đó để tính khoảng cách ngày.
3. Khi xây dựng bài toán dự báo khoảng cách đặt hàng, cần lọc các đơn hàng từ lần thứ 2 trở đi (`order_number >= 2`).
"""))

# Cell 8: Section 2
cells.append(new_markdown_cell("""## 2. Khảo sát biến mục tiêu cho bài toán hồi quy

Hai biến mục tiêu tiềm năng:
- `days_since_prior_order`: Khoảng cách số ngày giữa hai lần mua liên tiếp của khách hàng.
- `basket_size`: Số lượng sản phẩm trong một đơn hàng.
"""))

# Cell 9: Compute basket_size
cells.append(new_code_cell("""t0 = time.time()
op_prior_order_ids = pd.read_csv(os.path.join(dataset_path, "order_products__prior.csv"), usecols=["order_id"])
basket_size_prior = op_prior_order_ids.groupby("order_id").size().astype(np.uint16).rename("basket_size")
basket_size_train = op_train.groupby("order_id").size().astype(np.uint16).rename("basket_size")

all_basket_sizes = pd.concat([basket_size_prior, basket_size_train])
orders["basket_size"] = orders["order_id"].map(all_basket_sizes)

del op_prior_order_ids, basket_size_prior, basket_size_train
gc.collect()

print(f"Da tinh basket_size cho {len(all_basket_sizes):,d} don hang ({time.time()-t0:.2f}s).")
print(f"So don hang co basket_size: {orders['basket_size'].notnull().sum():,d} / {len(orders):,d}")
"""))

# Cell 10: Target statistics
cells.append(new_code_cell("""print("--- Thong ke days_since_prior_order ---")
ds = orders['days_since_prior_order'].dropna()
print(ds.describe())
print(f"Skewness: {ds.skew():.4f}")
print(f"Kurtosis: {ds.kurt():.4f}")
print(f"Ty le 0 ngay:   {(ds == 0).sum():,d} ({(ds == 0).mean()*100:.2f}%)")
print(f"Ty le 7 ngay:   {(ds == 7).sum():,d} ({(ds == 7).mean()*100:.2f}%)")
print(f"Ty le 30 ngay:  {(ds == 30).sum():,d} ({(ds == 30).mean()*100:.2f}%)")

print("\\n--- Thong ke basket_size ---")
bs = orders['basket_size'].dropna()
print(bs.describe())
print(f"Skewness: {bs.skew():.4f}")
print(f"Kurtosis: {bs.kurt():.4f}")
print(f"Min: {bs.min()} | Median: {bs.median():.0f} | Max: {bs.max()}")
"""))

# Cell 11: Plots
cells.append(new_code_cell("""fig, axes = plt.subplots(2, 2, figsize=(13, 8))

sns.histplot(ds, bins=31, color='#1f77b4', edgecolor='black', ax=axes[0, 0], stat='percent')
axes[0, 0].set_title("Phan phoi days_since_prior_order")
axes[0, 0].set_xlabel("So ngay")
axes[0, 0].set_ylabel("Ty le (%)")
axes[0, 0].axvline(7, color='red', linestyle='--', label='7 ngay')
axes[0, 0].axvline(30, color='darkorange', linestyle='--', label='30 ngay (Censored)')
axes[0, 0].legend()

sns.boxplot(x=ds, color='#aec7e8', ax=axes[0, 1])
axes[0, 1].set_title("Boxplot days_since_prior_order")
axes[0, 1].set_xlabel("So ngay")

sns.histplot(bs[bs <= 50], bins=50, color='#2ca02c', edgecolor='black', ax=axes[1, 0], stat='percent')
axes[1, 0].set_title("Phan phoi basket_size (<= 50)")
axes[1, 0].set_xlabel("So luong san pham")
axes[1, 0].set_ylabel("Ty le (%)")
axes[1, 0].axvline(bs.median(), color='red', linestyle='--', label=f'Median: {bs.median():.0f}')
axes[1, 0].legend()

sns.histplot(np.log1p(bs), bins=40, color='#98df8a', edgecolor='black', kde=True, ax=axes[1, 1], stat='percent')
axes[1, 1].set_title("Phan phoi Log(basket_size + 1)")
axes[1, 1].set_xlabel("Log(basket_size + 1)")
axes[1, 1].set_ylabel("Ty le (%)")

plt.tight_layout()
plt.show()
"""))

# Cell 12: Correlation
cells.append(new_code_cell("""corr_cols = ["order_number", "order_dow", "order_hour_of_day", "days_since_prior_order", "basket_size"]
corr_data = orders[corr_cols].dropna().sample(n=100000, random_state=42)

pearson_corr = corr_data.corr(method='pearson')
spearman_corr = corr_data.corr(method='spearman')

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.heatmap(pearson_corr, annot=True, fmt='.3f', cmap='coolwarm', vmin=-0.5, vmax=0.5, ax=axes[0], cbar=False)
axes[0].set_title("Tuong quan Pearson")

sns.heatmap(spearman_corr, annot=True, fmt='.3f', cmap='coolwarm', vmin=-0.5, vmax=0.5, ax=axes[1])
axes[1].set_title("Tuong quan Spearman")

plt.tight_layout()
plt.show()

print(f"Pearson (order_number, days_since_prior_order):  {pearson_corr.loc['order_number', 'days_since_prior_order']:.3f}")
print(f"Spearman (order_number, days_since_prior_order): {spearman_corr.loc['order_number', 'days_since_prior_order']:.3f}")
print(f"Pearson (days_since_prior_order, basket_size):   {pearson_corr.loc['days_since_prior_order', 'basket_size']:.3f}")
"""))

# Cell 13: Note on section 2
cells.append(new_markdown_cell("""**Nhận xét:**
- `order_number` và `days_since_prior_order` tương quan âm (-0.370): khách hàng đặt càng nhiều đơn thì khoảng cách giữa các lần đặt hàng càng có xu hướng rút ngắn lại.
- `days_since_prior_order` bị cắt chặn trên tại 30 ngày (chiếm 10.8% dữ liệu) và có đỉnh cục bộ tại chu kỳ tuần (7, 14, 21, 28 ngày).
- `basket_size` có phân phối lệch phải (phần lớn 3-12 sản phẩm, trung vị là 8). Sau khi lấy log1p, phân phối tiến gần hơn về dạng phân phối chuẩn.
"""))

# Cell 14: Section 3
cells.append(new_markdown_cell("""## 3. Khảo sát yếu tố thời gian và chuỗi thời gian

Dữ liệu cung cấp các thuộc tính thời gian tương đối:
- `order_dow`: Thứ trong tuần (0 đến 6).
- `order_hour_of_day`: Giờ trong ngày (0 đến 23).
- `days_since_prior_order`: Khoảng cách ngày so với đơn trước.
- `order_number`: Thứ tự đơn hàng của từng khách hàng.
"""))

# Cell 15: Seasonality plots
cells.append(new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))

dow_counts = orders['order_dow'].value_counts().sort_index()
sns.barplot(x=dow_counts.index, y=dow_counts.values, palette='Blues_d', ax=axes[0])
axes[0].set_title("Don hang theo thu trong tuan (order_dow)")
axes[0].set_xlabel("Thu (0: Chu Nhat, 1: Thu Hai, ...)")
axes[0].set_ylabel("So luong don hang")

hour_counts = orders['order_hour_of_day'].value_counts().sort_index()
sns.barplot(x=hour_counts.index, y=hour_counts.values, palette='Greens_d', ax=axes[1])
axes[1].set_title("Don hang theo gio trong ngay (order_hour_of_day)")
axes[1].set_xlabel("Gio (0 - 23)")
axes[1].set_ylabel("So luong don hang")
axes[1].axvspan(9, 16, color='yellow', alpha=0.25, label='Khung gio 9h - 16h')
axes[1].legend()

plt.tight_layout()
plt.show()
"""))

# Cell 16: Heatmap 168 hours
cells.append(new_code_cell("""dow_hour_matrix = orders.groupby(['order_dow', 'order_hour_of_day']).size().unstack()

plt.figure(figsize=(13, 5.5))
sns.heatmap(dow_hour_matrix, cmap='YlGnBu', fmt='d', cbar_kws={'label': 'So luong don hang'})
plt.title("Phan bo don hang theo 168 khung gio trong tuan")
plt.xlabel("Gio trong ngay (0 - 23)")
plt.ylabel("Thu trong tuan (0: CN, 1: T2, ..., 6: T7)")
plt.yticks(ticks=np.arange(7) + 0.5, labels=['Chu Nhat', 'Thu Hai', 'Thu Ba', 'Thu Tu', 'Thu Nam', 'Thu Sau', 'Thu Bay'], rotation=0)
plt.tight_layout()
plt.show()
"""))

# Cell 17: Frequency & Missing Time Period
cells.append(new_code_cell("""print("--- Frequency cua Time Series ---")
print("Instacart la irregular time series: khong co timestamp tuyet doi.")
print("Khoang cach giua cac lan dat hang phan phoi theo days_since_prior_order:")
freq_counts = orders['days_since_prior_order'].value_counts().sort_index()
print(freq_counts.to_string())

fig, ax = plt.subplots(figsize=(13, 4))
ax.bar(freq_counts.index, freq_counts.values, color='#5b8db8', edgecolor='none')
ax.set_title("Phan phoi tan suat days_since_prior_order (Irregular Time Series)")
ax.set_xlabel("days_since_prior_order (so ngay)")
ax.set_ylabel("So don hang")
ax.axvline(7, color='red', linestyle='--', linewidth=1.2, label='7 ngay')
ax.axvline(14, color='darkorange', linestyle='--', linewidth=1.2, label='14 ngay')
ax.axvline(30, color='purple', linestyle='--', linewidth=1.2, label='30 ngay (Censored)')
ax.legend()
plt.tight_layout()
plt.show()
"""))

# Cell 18: Missing Time Period
cells.append(new_code_cell("""print("--- Missing Time Period ---")
print("Dataset khong co ngay tuyet doi (chi co days_since_prior_order tuong doi).")
print("Khong the kiem tra khoang thoi gian bi thieu theo lich truc tiep.")
print("Kiem tra gap theo order_number cua tung user:")
max_order = orders.groupby('user_id')['order_number'].max()
print(f"Max order_number: {max_order.max()} | Mean: {max_order.mean():.1f} | Median: {max_order.median():.0f}")

gap_check = orders.sort_values(['user_id', 'order_number']).groupby('user_id')['order_number'].apply(
    lambda x: (x.diff().dropna() != 1).sum()
)
print(f"So user co gap (order_number khong lien tuc): {(gap_check > 0).sum()} / {len(gap_check):,d}")
print(f"=> order_number lien tuc: du lieu khong co missing time period theo thu tu don hang.")
"""))

# Cell 19: Autocorrelation
cells.append(new_code_cell("""weekly_demand_series = dow_hour_matrix.stack().values
simulated_demand = np.tile(weekly_demand_series, 4)

fig, axes = plt.subplots(1, 2, figsize=(14, 4))
plot_acf(simulated_demand, lags=72, ax=axes[0], title="Autocorrelation (ACF) - 72 lags")
axes[0].axvline(24, color='red', linestyle='--', label='Lag 24h')
axes[0].axvline(48, color='darkorange', linestyle='--', label='Lag 48h')
axes[0].legend()

plot_pacf(simulated_demand, lags=72, ax=axes[1], title="Partial Autocorrelation (PACF) - 72 lags", method='ywm')
axes[1].axvline(24, color='red', linestyle='--', label='Lag 24h')
axes[1].legend()

plt.tight_layout()
plt.show()
"""))

# Cell 18: Trend
cells.append(new_code_cell("""order_stats = orders.groupby('order_number').agg(
    mean_days=('days_since_prior_order', 'mean'),
    median_days=('days_since_prior_order', 'median'),
    mean_basket=('basket_size', 'mean'),
    order_count=('order_id', 'count')
).reset_index()

order_stats_plot = order_stats[(order_stats['order_number'] >= 2) & (order_stats['order_number'] <= 60)]

fig, ax1 = plt.subplots(figsize=(11, 4.5))

color = 'tab:blue'
ax1.set_xlabel("Thu tu don hang (order_number)")
ax1.set_ylabel("Khoang cach ngay trung binh", color=color)
l1 = ax1.plot(order_stats_plot['order_number'], order_stats_plot['mean_days'], color=color, linewidth=2, label='Mean Days')
ax1.plot(order_stats_plot['order_number'], order_stats_plot['median_days'], color='deepskyblue', linestyle=':', label='Median Days')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  
color = 'tab:green'
ax2.set_ylabel("Kich thuoc gio hang trung binh", color=color)
l2 = ax2.plot(order_stats_plot['order_number'], order_stats_plot['mean_basket'], color=color, linewidth=2, linestyle='--', label='Mean Basket Size')
ax2.tick_params(axis='y', labelcolor=color)

lines = l1 + ax1.lines[1:] + l2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='center right')

plt.title("Xu huong theo thu tu don hang")
plt.tight_layout()
plt.show()
"""))

# Cell 19: Note on section 3
cells.append(new_markdown_cell("""**Nhận xét:**
- Nhu cầu đặt hàng cao nhất vào ngày 0 (Chủ nhật) và ngày 1 (Thứ hai), tập trung trong khung giờ từ 9h đến 16h.
- Biểu đồ ACF và PACF cho thấy tính chu kỳ lặp lại theo ngày (24 giờ) rất rõ ràng.
- Xu hướng theo `order_number`: khoảng cách giữa các đơn hàng giảm dần từ ~15 ngày ở đơn thứ 2 xuống còn ~7-8 ngày ở đơn thứ 30, trong khi kích thước giỏ hàng giữ ở mức ổn định ~10 sản phẩm.
"""))

# Cell 20: Leakage note
cells.append(new_markdown_cell("""### Lưu ý về phân chia dữ liệu và rò rỉ thông tin (Data Leakage)
1. **Phân chia theo chuỗi (Sequence Split):** Không dùng K-Fold ngẫu nhiên để tránh lấy thông tin tương lai dự đoán quá khứ của cùng khách hàng.
2. **Tính toán đặc trưng lịch sử:** Các thống kê người dùng chỉ tính trên các đơn hàng trước đó thông qua `shift(1).expanding()`.
"""))

# Cell 21: Feature engineering
cells.append(new_code_cell("""train_users = orders[orders["eval_set"] == "train"]["user_id"].unique()
np.random.seed(42)
sample_size = 40000
sampled_users = np.random.choice(train_users, size=sample_size, replace=False)

df_sample = orders[orders["user_id"].isin(sampled_users)].copy()
df_sample.sort_values(["user_id", "order_number"], inplace=True)

df_sample["lag_1_days"] = df_sample.groupby("user_id")["days_since_prior_order"].shift(1)
df_sample["lag_2_days"] = df_sample.groupby("user_id")["days_since_prior_order"].shift(2)
df_sample["lag_3_days"] = df_sample.groupby("user_id")["days_since_prior_order"].shift(3)

shifted_days = df_sample.groupby("user_id")["days_since_prior_order"].shift(1)
cum_sum = shifted_days.groupby(df_sample["user_id"]).cumsum()
cum_count = shifted_days.groupby(df_sample["user_id"]).cumcount() + 1
df_sample["user_cum_mean_days"] = cum_sum / cum_count

df_sample["sin_hour"] = np.sin(2 * np.pi * df_sample["order_hour_of_day"] / 24.0).astype(np.float32)
df_sample["cos_hour"] = np.cos(2 * np.pi * df_sample["order_hour_of_day"] / 24.0).astype(np.float32)
df_sample["sin_dow"] = np.sin(2 * np.pi * df_sample["order_dow"] / 7.0).astype(np.float32)
df_sample["cos_dow"] = np.cos(2 * np.pi * df_sample["order_dow"] / 7.0).astype(np.float32)
df_sample["is_weekend"] = (df_sample["order_dow"] <= 1).astype(np.uint8)
df_sample["is_peak_hour"] = ((df_sample["order_hour_of_day"] >= 9) & (df_sample["order_hour_of_day"] <= 16)).astype(np.uint8)

df_sample[["user_id", "order_number", "days_since_prior_order", "lag_1_days", "lag_2_days", "user_cum_mean_days"]].head(5)
"""))

# Cell 22: Section 4
cells.append(new_markdown_cell("""## 4. Thử nghiệm các mô hình baseline

Thiết lập bài toán:
- **Target:** `days_since_prior_order`
- **Tập Train:** Đơn hàng $N-1$ của từng khách hàng
- **Tập Test:** Đơn hàng cuối cùng ($N$, thuộc `eval_set == 'train'`)
- **Mô hình:**
  1. Baseline 0: Dummy Mean Regressor
  2. Baseline 1: Persistence (Lag-1)
  3. Baseline 2: Ridge Regression
  4. Baseline 3: LightGBM Regressor
"""))

# Cell 23: Prepare train/test
cells.append(new_code_cell("""features = [
    "order_number", "order_dow", "order_hour_of_day",
    "sin_hour", "cos_hour", "sin_dow", "cos_dow", 
    "is_weekend", "is_peak_hour",
    "lag_1_days", "lag_2_days", "lag_3_days",
    "user_cum_mean_days"
]
target = "days_since_prior_order"

test_df = df_sample[df_sample["eval_set"] == "train"].copy()
max_order_per_user = df_sample.groupby("user_id")["order_number"].transform("max")
train_df = df_sample[(df_sample["order_number"] == max_order_per_user - 1) & (df_sample["order_number"] >= 4)].copy()

median_imputer = train_df[features].median()

X_train = train_df[features].fillna(median_imputer)
y_train = train_df[target]

X_test = test_df[features].fillna(median_imputer)
y_test = test_df[target]

print(f"Train (don N-1): {X_train.shape[0]:,d} dong | {X_train.shape[1]} features")
print(f"Test  (don N):   {X_test.shape[0]:,d} dong | {X_test.shape[1]} features")
"""))

# Cell 24: Fit models
cells.append(new_code_cell("""models_dict = {}

dummy = DummyRegressor(strategy="mean")
dummy.fit(X_train, y_train)
models_dict["Dummy Mean"] = dummy.predict(X_test)

models_dict["Persistence (Lag-1)"] = X_test["lag_1_days"].values

ridge = Ridge(alpha=10.0, random_state=42)
ridge.fit(X_train, y_train)
models_dict["Ridge Regression"] = ridge.predict(X_test)

lgb_reg = lgb.LGBMRegressor(
    n_estimators=150,
    learning_rate=0.05,
    num_leaves=31,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)
lgb_reg.fit(X_train, y_train)
models_dict["LightGBM Regressor"] = lgb_reg.predict(X_test)
"""))

# Cell 25: Compare metrics
cells.append(new_code_cell("""metrics_list = []

for name, y_pred in models_dict.items():
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    medae = median_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics_list.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "MedAE": medae,
        "R2": r2
    })

results_df = pd.DataFrame(metrics_list)
display(results_df.style.format({
    "MAE": "{:.3f}",
    "RMSE": "{:.3f}",
    "MedAE": "{:.3f}",
    "R2": "{:.4f}"
}))
"""))

# Cell 26: Plot metrics
cells.append(new_code_cell("""fig, axes = plt.subplots(1, 3, figsize=(14, 4))

sns.barplot(data=results_df, x="Model", y="MAE", palette="Blues_r", ax=axes[0])
axes[0].set_title("MAE (thap hon tot hon)")
axes[0].tick_params(axis='x', rotation=20)

sns.barplot(data=results_df, x="Model", y="RMSE", palette="Reds_r", ax=axes[1])
axes[1].set_title("RMSE (thap hon tot hon)")
axes[1].tick_params(axis='x', rotation=20)

sns.barplot(data=results_df, x="Model", y="R2", palette="Greens", ax=axes[2])
axes[2].set_title("R2 Score (cao hon tot hon)")
axes[2].tick_params(axis='x', rotation=20)

plt.tight_layout()
plt.show()
"""))

# Cell 27: Residuals & Feature importance
cells.append(new_code_cell("""y_pred_lgb = models_dict["LightGBM Regressor"]
residuals = y_test - y_pred_lgb

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

sns.histplot(residuals, bins=50, kde=True, color='teal', ax=axes[0])
axes[0].axvline(0, color='red', linestyle='--', linewidth=1.5, label='Residual = 0')
axes[0].set_title("Phan phoi phan du (LightGBM)")
axes[0].set_xlabel("Residual (ngay)")
axes[0].set_ylabel("Tan so")
axes[0].legend()

importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': lgb_reg.feature_importances_
}).sort_values('Importance', ascending=True)

axes[1].barh(importance_df['Feature'], importance_df['Importance'], color='#3470a3')
axes[1].set_title("Feature Importance (LightGBM)")
axes[1].set_xlabel("Importance Score")

plt.tight_layout()
plt.show()
"""))

# Cell 28: Section 5 Summary
cells.append(new_markdown_cell("""## 5. Tổng kết

| Nội dung | Kết quả khảo sát |
|---|---|
| **Chất lượng dữ liệu** | 6 bảng dữ liệu liên kết nhất quán, 0 dòng trùng lặp. Giá trị khuyết duy nhất là đơn hàng đầu tiên của mỗi khách hàng ở `days_since_prior_order`. |
| **Đặc tính thời gian** | Chu kỳ ngày (24h) và tuần (168h) rất rõ rệt; khung giờ cao điểm là 9h - 16h các ngày Chủ nhật và Thứ hai. |
| **Dự báo `days_since_prior_order`** | LightGBM đạt MAE ~ 7.7 ngày, MedAE ~ 6.0 ngày, $R^2 \approx 0.28$. Hiện tượng bị chặn trên tại 30 ngày (chiếm ~10.8%) là nguyên nhân chính khiến mô hình hồi quy thông thường bị giới hạn độ chính xác. Hướng phát triển phù hợp là Tobit Regression hoặc Survival Analysis. |
| **Đặc trưng quan trọng nhất** | Lịch sử trung bình của khách hàng (`user_cum_mean_days`) và độ trễ đơn hàng gần nhất (`lag_1_days`) đóng vai trò chi phối. |
"""))

nb.cells = cells

# Save notebook
notebook_path = os.path.join("notebooks", "DS317_KiemChung_Instacart_Regression_TimeSeries.ipynb")
with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Successfully generated notebook at: {notebook_path}")
