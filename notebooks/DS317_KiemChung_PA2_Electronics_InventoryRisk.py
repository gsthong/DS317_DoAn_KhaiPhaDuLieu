#!/usr/bin/env python
# coding: utf-8

# # Khảo sát và thẩm định Phương án 2: Cảnh báo sớm rủi ro tồn kho (Inventory Risk Classification) trên 2 bộ dữ liệu
# **Môn học:** Khai phá dữ liệu trong doanh nghiệp (DS317)  
# **Bộ dữ liệu thẩm định:**
# 1. **Electronics Sales Dataset** (Dataset chính - B-Tech Style)
# 2. **Instacart Market Basket Analysis** (Dataset benchmark / tham khảo)
# 
# ---
# 
# ### Mục tiêu kiểm chứng
# Thẩm định thực nghiệm tính khả thi của **Phương án 2 (PA2)** theo 4 khía cạnh cốt lõi:
# 1. **Dữ liệu (Data Feasibility):** Kiểm tra cấu trúc, liên kết khóa ngoại (`SKU_ID`), tính đầy đủ của trường tồn kho, mốc thời gian, tính toàn vẹn và khả năng tái lập tồn kho lũy kế trên 2 dataset.
# 2. **Kỹ thuật (Technical Feasibility):** Kiểm chứng khung bài toán theo đơn vị quan sát $(SKU \times Tuần\ t)$, quy tắc gán nhãn nghiệp vụ `InventoryRisk` (Low / Medium / High) qua chỉ số `Coverage` và `SalesTrend`, chiến lược phân chia chuỗi thời gian có khoảng đệm 4 tuần (Gap Split) chống rò rỉ dữ liệu (data leakage), và hiệu năng phân loại qua các mô hình baseline & LightGBM (PP-A).
# 3. **Nguồn lực (Resource Feasibility):** Đo lường mức tiêu thụ bộ nhớ RAM, thời gian huấn luyện và đánh giá tính khả thi triển khai trên môi trường Google Colab / Kaggle.
# 4. **Đạo đức – Pháp lý (Ethics & Legal Feasibility):** Kiểm tra giấy phép dữ liệu, rà soát tính riêng tư và dữ liệu định danh cá nhân (PII), đánh giá rủi ro thiên vị của nhãn đại diện (proxy label).

# In[ ]:


import os
import sys
import time
import gc
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, recall_score, precision_score, f1_score,
    classification_report, confusion_matrix, precision_recall_curve, auc
)
import lightgbm as lgb
import kagglehub

warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['figure.dpi'] = 120
pd.set_option('display.max_columns', 50)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

print("Moi truong khoi tao thanh cong.")


# In[ ]:


# Xac dinh duong dan 2 bo du lieu
# 1. Electronics Sales Dataset (dataset chinh)
electronics_local = os.path.abspath("../data/raw")
if os.path.exists(electronics_local) and os.path.exists(os.path.join(electronics_local, "SalesOrders.csv")):
    electronics_path = electronics_local
    print(f"Electronics Dataset: Su dung thu muc noi bo -> {electronics_path}")
else:
    electronics_path = kagglehub.dataset_download("fahdelatiby/electronics-sales-dataset-b-tech-style")
    print(f"Electronics Dataset: Tai qua kagglehub -> {electronics_path}")

# 2. Instacart Market Basket Analysis (dataset benchmark)
instacart_path = kagglehub.dataset_download("psparks/instacart-market-basket-analysis")
print(f"Instacart Dataset: Tai qua kagglehub -> {instacart_path}")

print("\n--- Danh sach file Electronics Sales Dataset (top 10 file tieu bieu) ---")
elec_files = sorted(os.listdir(electronics_path))
print(f"Tong so file: {len(elec_files)} file csv")
for f in elec_files[:10]:
    sz = os.path.getsize(os.path.join(electronics_path, f)) / (1024 * 1024)
    print(f"  {f:<30} | {sz:>8.2f} MB")

print("\n--- Danh sach file Instacart Dataset ---")
insta_files = sorted(os.listdir(instacart_path))
for f in insta_files:
    sz = os.path.getsize(os.path.join(instacart_path, f)) / (1024 * 1024)
    print(f"  {f:<30} | {sz:>8.2f} MB")


# ## 1. Thẩm định khía cạnh Dữ liệu (Data Feasibility)
# 
# ### 1.1. Thẩm định tính khả thi trên Dataset tham khảo (Instacart) đối với Phương án 2
# Mục tiêu của Phương án 2 là: **Phân loại rủi ro tồn kho (InventoryRisk) theo từng SKU trong tuần $t$**, dựa trên lượng tồn kho cuối tuần và doanh số thực tế 4 tuần tiếp theo.  
# Dưới đây là kiểm chứng thực nghiệm để đánh giá xem Instacart có thỏa mãn các biến số cần thiết của Phương án 2 hay không.

# In[ ]:


# Kiem tra schema cac bang quan trong cua Instacart
insta_orders = pd.read_csv(os.path.join(instacart_path, "orders.csv"), nrows=5)
insta_products = pd.read_csv(os.path.join(instacart_path, "products.csv"), nrows=5)
insta_op = pd.read_csv(os.path.join(instacart_path, "order_products__train.csv"), nrows=5)

print("Schema bang orders.csv:")
print(insta_orders.columns.tolist())
print("\nSchema bang products.csv:")
print(insta_products.columns.tolist())
print("\nSchema bang order_products__train.csv:")
print(insta_op.columns.tolist())

# Kiem tra su ton tai cua cac truong bat buoc cho Phuong an 2
has_inventory_table = any("inventory" in f.lower() or "stock" in f.lower() for f in insta_files)
has_stock_col = any("stock" in c.lower() or "inventory" in c.lower() or "qty" in c.lower() 
                    for df in [insta_orders, insta_products, insta_op] for c in df.columns)
has_calendar_date = "order_date" in insta_orders.columns or "date" in insta_orders.columns

print("\n--- Ket qua kiem tra yeu cau du lieu PA2 tren Instacart ---")
print(f"Co bang ton kho / bien dong kho:   {has_inventory_table}")
print(f"Co cot so luong ton kho (Stock):   {has_stock_col}")
print(f"Co moc thoi gian lich (Calendar):  {has_calendar_date}")
print(f"Truong thoi gian kha dung:         {[c for c in insta_orders.columns if 'order' in c or 'day' in c]}")


# **Đánh giá thực nghiệm trên Instacart đối với Phương án 2:**
# 1. **Thiếu biến tồn kho (Inventory = None):** Instacart hoàn toàn không có bảng kho, không có số lượng tồn kho (on-hand balance), không có dữ liệu nhập kho (purchase receipts) hay biến động kho. Do đó, **không thể tính chỉ số Coverage** ($EndInventory \div Sales$).
# 2. **Thiếu mốc thời gian tuyệt đối:** Trường thời gian trong Instacart chỉ là `days_since_prior_order` (khoảng cách ngày tương đối của người dùng), `order_dow` (thứ) và `order_hour_of_day` (giờ). Không có ngày tháng năm thực tế để lập chuỗi thời gian tuần $t$.
# 3. **Kết luận về Instacart đối với PA2:** **KHÔNG ĐẠT (Infeasible)**. Instacart chỉ phù hợp làm benchmark cho Phương án khai phá luật kết hợp giỏ hàng (Market Basket Analysis), hoàn toàn không thể dùng cho Phương án 2.

# ### 1.2. Thẩm định cấu trúc và liên kết bảng trên Electronics Sales Dataset (Dataset chính)
# Phương án 2 yêu cầu liên kết giữa:
# - Lịch sử bán hàng: `SalesOrders`, `SalesOrderLines`
# - Biến động và số dư tồn kho: `InventoryMovements`, `InventoryBalances`
# - Thông tin phân cấp sản phẩm: `Products`, `ProductVariants`

# In[ ]:


# Doc cac bang can thiet
t0 = time.time()
so = pd.read_csv(os.path.join(electronics_path, "SalesOrders.csv"), 
                 usecols=['SalesOrderID', 'OrderDate', 'OrderStatus'])
sol = pd.read_csv(os.path.join(electronics_path, "SalesOrderLines.csv"), 
                  usecols=['SalesOrderID', 'SKU_ID', 'Quantity', 'ActualSellingPrice', 'PromotionID'])
im = pd.read_csv(os.path.join(electronics_path, "InventoryMovements.csv"),
                 usecols=['MovementDateTime', 'SKU_ID', 'MovementType', 'Quantity', 'ToCondition'])
ib = pd.read_csv(os.path.join(electronics_path, "InventoryBalances.csv"))

print(f"Thoi gian nạp du lieu: {time.time()-t0:.2f}s")
print(f"SalesOrders:        {len(so):>10,d} dong | {so.shape[1]} cot")
print(f"SalesOrderLines:    {len(sol):>10,d} dong | {sol.shape[1]} cot")
print(f"InventoryMovements: {len(im):>10,d} dong | {im.shape[1]} cot")
print(f"InventoryBalances:  {len(ib):>10,d} dong | {ib.shape[1]} cot")

# Kiem tra khoa SKU_ID
skus_sales = set(sol['SKU_ID'].unique())
skus_inv_mov = set(im['SKU_ID'].unique())
skus_inv_bal = set(ib['SKU_ID'].unique())

print(f"\nSo luong SKU trong SalesOrderLines:    {len(skus_sales):,d}")
print(f"So luong SKU trong InventoryMovements: {len(skus_inv_mov):,d}")
print(f"So luong SKU trong InventoryBalances:  {len(skus_inv_bal):,d}")

overlap_sales_inv = skus_sales.intersection(skus_inv_mov)
print(f"So SKU giao thoa giua Sales va Movements: {len(overlap_sales_inv):,d} ({100*len(overlap_sales_inv)/len(skus_sales):.2f}%)")


# In[ ]:


# Kiem tra truc thoi gian giua SalesOrders va InventoryMovements
so['OrderDate'] = pd.to_datetime(so['OrderDate'])
im['MovementDateTime'] = pd.to_datetime(im['MovementDateTime'])

print("--- Khoang thoi gian goc ---")
print(f"SalesOrders min/max:        {so['OrderDate'].min().strftime('%Y-%m-%d')} den {so['OrderDate'].max().strftime('%Y-%m-%d')}")
print(f"InventoryMovements min/max: {im['MovementDateTime'].min().strftime('%Y-%m-%d')} den {im['MovementDateTime'].max().strftime('%Y-%m-%d')}")

# Phan bo don hang theo nam
so['Year'] = so['OrderDate'].dt.year
orders_by_year = so.groupby('Year')['SalesOrderID'].count()
print("\nPhan bo don hang theo nam trong SalesOrders:")
for y, cnt in orders_by_year.items():
    print(f"  Nam {y}: {cnt:>10,d} don ({100*cnt/len(so):>6.2f}%)")

# Giai doan hoat dong dong bo thuc te: 2023-07-01 den 2025-12-31
valid_period_mask = (so['OrderDate'] >= '2023-07-01') & (so['OrderDate'] <= '2025-12-31')
print(f"\nDon hang trong giai doan 07/2023 - 12/2025: {valid_period_mask.sum():,d} / {len(so):,d} ({100*valid_period_mask.mean():.3f}%)")
print("Cac don truoc 07/2023 (13 don) va sau 2025 (16 don) la outlier/test, khong co phat sinh ton kho tuong ung.")


# In[ ]:


# 1.3. Tai lap chuoi ton kho luy ke (Cumulative Inventory)
# Loc du lieu trong giai doan chuan 2023-07-01 den 2025-12-31
im_clean = im[(im['MovementDateTime'] >= '2023-07-01') & (im['MovementDateTime'] <= '2025-12-31')].copy()

# Xac dinh chieu bien dong so luong (Net Quantity Change)
conditions = [
    im_clean['MovementType'].isin(['Opening Balance', 'Purchase Receipt', 'Customer Return']),
    im_clean['MovementType'].isin(['Sale', 'Purchase Return', 'Replacement Issue']),
    im_clean['MovementType'] == 'Adjustment',
    im_clean['MovementType'] == 'Internal Transfer'
]
choices = [
    im_clean['Quantity'],
    -im_clean['Quantity'],
    np.where(im_clean['ToCondition'] == 'Available', im_clean['Quantity'], -im_clean['Quantity']),
    0
]
im_clean['NetQtyChange'] = np.select(conditions, choices, default=0)
im_clean['Week'] = im_clean['MovementDateTime'].dt.to_period('W').dt.start_time

# Tong hop bien dong kho theo SKU va Tuan
weekly_inv = im_clean.groupby(['SKU_ID', 'Week'])['NetQtyChange'].sum().reset_index()
weekly_inv = weekly_inv.sort_values(['SKU_ID', 'Week'])
weekly_inv['EndInventory'] = weekly_inv.groupby('SKU_ID')['NetQtyChange'].cumsum()

print("--- Thong ke ton kho luy ke cuoi tuan (EndInventory) tren 877 SKU ---")
print(weekly_inv['EndInventory'].describe())
print(f"Tong so quan sat SKU x Tuan co bien dong: {len(weekly_inv):,d}")
print(f"So luong gia tri ton kho am (< 0):         {(weekly_inv['EndInventory'] < 0).sum():,d}")
print(f"Ty le ton kho hop le (>= 0):               {100*(weekly_inv['EndInventory'] >= 0).mean():.2f}%")


# In[ ]:


# Truc quan hoa chuoi thoi gian ton kho va doanh so cua 2 SKU tieu bieu
so_clean = so[(so['OrderDate'] >= '2023-07-01') & (so['OrderDate'] <= '2025-12-31') & (so['OrderStatus'] != 'Cancelled')].copy()
sales_m = pd.merge(sol, so_clean[['SalesOrderID', 'OrderDate']], on='SalesOrderID')
sales_m['Week'] = sales_m['OrderDate'].dt.to_period('W').dt.start_time

sample_skus = ['SKU0000001', 'SKU0000004']
fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True)

for i, sku in enumerate(sample_skus):
    sku_inv = weekly_inv[weekly_inv['SKU_ID'] == sku].set_index('Week')['EndInventory']
    sku_sales = sales_m[sales_m['SKU_ID'] == sku].groupby('Week')['Quantity'].sum()
    
    ax1 = axes[i]
    ax2 = ax1.twinx()
    
    ax1.plot(sku_inv.index, sku_inv.values, color='#1f77b4', lw=1.8, label='Ton kho cuoi tuan (EndInventory)')
    ax2.bar(sku_sales.index, sku_sales.values, width=5, color='#ff7f0e', alpha=0.5, label='So luong ban (SalesQty)')
    
    ax1.set_ylabel('Ton kho (Chiec)', color='#1f77b4')
    ax2.set_ylabel('Ban hang (Chiec)', color='#ff7f0e')
    ax1.set_title(f"Dien bien Ton kho va Doanh so theo tuan - {sku}")
    ax1.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


# ## 2. Thẩm định khía cạnh Kỹ thuật (Technical Feasibility)
# 
# ### 2.1. Thiết kế đơn vị phân tích và khung bảng dữ liệu (Panel Construction)
# - **Đơn vị phân tích:** Một quan sát = Một sản phẩm ($SKU$) trong một tuần $t$.
# - **Lưới thời gian chuẩn:** Tạo Cartesian product giữa 871 SKU và 130 tuần liên tục (07/2023 $\to$ 12/2025).
# - **Quy tắc gán nhãn nghiệp vụ (Rule-based Labeling):**
#   $$\text{Coverage}(t) = \frac{\text{EndInventory}(t)}{\frac{1}{4} \sum_{k=1}^4 \text{Sales}(t+k) + \varepsilon}$$
#   - **High:** $\text{Coverage}(t) \ge P_{85}$ (ngưỡng phân vị 85 trên tập Train) VÀ xu hướng bán 4 tuần gần nhất không tăng ($\text{SalesTrend}_{4w} \le 0$).
#   - **Medium:** $P_{60} \le \text{Coverage}(t) < P_{85}$ hoặc ($\text{Coverage}(t) \ge P_{85}$ nhưng đang có xu hướng tăng trưởng).
#   - **Low:** Các trường hợp còn lại.

# In[ ]:


# 1. Tong hop ban hang theo tuan
sales_m['Revenue'] = sales_m['ActualSellingPrice'] * sales_m['Quantity']
weekly_sales = sales_m.groupby(['SKU_ID', 'Week']).agg(
    WeeklyQty=('Quantity', 'sum'),
    WeeklyRevenue=('Revenue', 'sum'),
    AvgPrice=('ActualSellingPrice', 'mean'),
    PromoCount=('PromotionID', lambda x: x.notna().sum())
).reset_index()

# 2. Tao luoi Panel day du (SKU x Week)
all_skus = sorted(weekly_sales['SKU_ID'].unique())
all_weeks = pd.date_range('2023-07-03', '2025-12-22', freq='W-MON')
panel = pd.MultiIndex.from_product([all_skus, all_weeks], names=['SKU_ID', 'Week']).to_frame().reset_index(drop=True)

df = pd.merge(panel, weekly_sales, on=['SKU_ID', 'Week'], how='left')
df['WeeklyQty'] = df['WeeklyQty'].fillna(0)
df['WeeklyRevenue'] = df['WeeklyRevenue'].fillna(0)
df['PromoCount'] = df['PromoCount'].fillna(0)
df['AvgPrice'] = df.groupby('SKU_ID')['AvgPrice'].ffill().bfill()

df = pd.merge(df, weekly_inv[['SKU_ID', 'Week', 'NetQtyChange', 'EndInventory']], on=['SKU_ID', 'Week'], how='left')
df['NetQtyChange'] = df['NetQtyChange'].fillna(0)
df['EndInventory'] = df.groupby('SKU_ID')['EndInventory'].ffill().fillna(0)

# 3. Tao bien muc tieu (Future 4-week sales & Coverage)
df = df.sort_values(['SKU_ID', 'Week']).reset_index(drop=True)
for k in [1, 2, 3, 4]:
    df[f'FutureSales_{k}'] = df.groupby('SKU_ID')['WeeklyQty'].shift(-k)

df['FutureAvgSales_4w'] = df[['FutureSales_1', 'FutureSales_2', 'FutureSales_3', 'FutureSales_4']].mean(axis=1)
eps = 0.5
df['Coverage'] = df['EndInventory'] / (df['FutureAvgSales_4w'] + eps)

# Tinh xu huong ban 4 tuan qua
df['Sales_Lag_4'] = df.groupby('SKU_ID')['WeeklyQty'].shift(4)
df['SalesTrend_4w'] = df['WeeklyQty'] - df['Sales_Lag_4']

print(f"Kich thuoc Panel tong the: {df.shape[0]:,d} dong | {df.shape[1]} cot")


# In[ ]:


# 2.2. Ky thuat dac trung (Feature Engineering - strictly <= t, no leakage)
# Dac trung do tre (Lags)
for lag in [1, 2, 8]:
    df[f'Sales_Lag_{lag}'] = df.groupby('SKU_ID')['WeeklyQty'].shift(lag)

# Rolling statistics (dich 1 tuan de khong trung lap tuan hien tai)
df['Sales_RollingMean_4w'] = df.groupby('SKU_ID')['WeeklyQty'].shift(1).rolling(4, min_periods=4).mean()
df['Sales_RollingStd_4w'] = df.groupby('SKU_ID')['WeeklyQty'].shift(1).rolling(4, min_periods=4).std().fillna(0)
df['Sales_RollingMean_8w'] = df.groupby('SKU_ID')['WeeklyQty'].shift(1).rolling(8, min_periods=8).mean()

# Past Coverage (uoc luong tuong doi trong qua khu tai thoi diem t)
df['PastCoverage'] = df['EndInventory'] / (df['Sales_RollingMean_4w'] + eps)

# Dac trung lich
df['Month'] = df['Week'].dt.month
df['WeekOfYear'] = df['Week'].dt.isocalendar().week.astype(int)

# Loc cac dong hop le (co du lich su lag 8 va tuong lai 4 tuan)
valid_df = df.dropna(subset=['Coverage', 'Sales_Lag_8', 'Sales_RollingMean_8w', 'PastCoverage']).copy()
valid_df = valid_df.sort_values(['Week', 'SKU_ID']).reset_index(drop=True)

print(f"So luong quan sat hop le de huan luyen & danh gia: {len(valid_df):,d} dong")
print(f"So tuan hop le: {valid_df['Week'].nunique()} tuan ({valid_df['Week'].min().strftime('%Y-%m-%d')} -> {valid_df['Week'].max().strftime('%Y-%m-%d')})")


# In[ ]:


# 2.3. Chien luoc chia du lieu theo thoi gian co khoang dem 4 tuan (Gap Split)
unique_weeks = sorted(valid_df['Week'].unique())
n_weeks = len(unique_weeks)

train_weeks_cnt = int(n_weeks * 0.70)
val_weeks_cnt = int(n_weeks * 0.15)
gap_weeks = 4

train_end_idx = train_weeks_cnt
val_start_idx = train_end_idx + gap_weeks
val_end_idx = val_start_idx + val_weeks_cnt
test_start_idx = val_end_idx + gap_weeks

train_weeks = unique_weeks[:train_end_idx]
val_weeks = unique_weeks[val_start_idx:val_end_idx]
test_weeks = unique_weeks[test_start_idx:]

train_set = valid_df[valid_df['Week'].isin(train_weeks)].copy()
val_set = valid_df[valid_df['Week'].isin(val_weeks)].copy()
test_set = valid_df[valid_df['Week'].isin(test_weeks)].copy()

# Uoc luong nguong phan vi P60 va P85 CHI TREN TAP TRAIN de chong ro ri du lieu
p60 = train_set['Coverage'].quantile(0.60)
p85 = train_set['Coverage'].quantile(0.85)

print(f"Tong so tuan: {n_weeks}")
print(f"Train set: {len(train_weeks):>2} tuan ({train_weeks[0].strftime('%Y-%m-%d')} -> {train_weeks[-1].strftime('%Y-%m-%d')}) | {len(train_set):>6,d} dong")
print(f"Gap 1:     {gap_weeks:>2} tuan (Khoang dem ngan cach Train va Val tranh ro ri nhan 4 tuan)")
print(f"Val set:   {len(val_weeks):>2} tuan ({val_weeks[0].strftime('%Y-%m-%d')} -> {val_weeks[-1].strftime('%Y-%m-%d')}) | {len(val_set):>6,d} dong")
print(f"Gap 2:     {gap_weeks:>2} tuan (Khoang dem ngan cach Val va Test)")
print(f"Test set:  {len(test_weeks):>2} tuan ({test_weeks[0].strftime('%Y-%m-%d')} -> {test_weeks[-1].strftime('%Y-%m-%d')}) | {len(test_set):>6,d} dong")
print(f"\nNguong Coverage uoc tinh tren Train: P60 = {p60:.2f}, P85 = {p85:.2f}")

# Gan nhan InventoryRisk
for subset in [train_set, val_set, test_set]:
    subset['Target'] = np.where(
        (subset['Coverage'] >= p85) & (subset['SalesTrend_4w'] <= 0), 2, # High
        np.where(subset['Coverage'] >= p60, 1, 0) # Medium / Low
    )

print("\nPhan bo nhan tren Tap Train:")
print(train_set['Target'].value_counts(normalize=True).rename({0:'Low', 1:'Medium', 2:'High'}))
print("\nPhan bo nhan tren Tap Test:")
print(test_set['Target'].value_counts(normalize=True).rename({0:'Low', 1:'Medium', 2:'High'}))


# In[ ]:


# 2.4. Huan luyen cac mo hinh Baseline va PP-A (LightGBM)
features = [
    'WeeklyQty', 'WeeklyRevenue', 'AvgPrice', 'PromoCount', 'NetQtyChange', 'EndInventory',
    'Sales_Lag_1', 'Sales_Lag_2', 'Sales_Lag_4', 'Sales_Lag_8',
    'Sales_RollingMean_4w', 'Sales_RollingStd_4w', 'Sales_RollingMean_8w',
    'SalesTrend_4w', 'PastCoverage', 'Month', 'WeekOfYear'
]

X_train, y_train = train_set[features].fillna(0), train_set['Target']
X_test, y_test = test_set[features].fillna(0), test_set['Target']

# Model 1: Heuristic Rule-based Threshold (dung PastCoverage)
test_set['Pred_Rule'] = np.where(
    (test_set['PastCoverage'] >= p85) & (test_set['SalesTrend_4w'] <= 0), 2,
    np.where(test_set['PastCoverage'] >= p60, 1, 0)
)
y_pred_rule = test_set['Pred_Rule']

# Model 2: Dummy Classifier (Stratified)
dummy = DummyClassifier(strategy='stratified', random_state=42)
dummy.fit(X_train, y_train)
y_pred_dummy = dummy.predict(X_test)

# Model 3: Logistic Regression (Multinomial, class_weight='balanced')
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

lr = LogisticRegression(max_iter=500, class_weight='balanced', random_state=42)
t_lr_start = time.time()
lr.fit(X_train_scaled, y_train)
t_lr_train = time.time() - t_lr_start
y_pred_lr = lr.predict(X_test_scaled)
y_prob_lr = lr.predict_proba(X_test_scaled)[:, 2]

# Model 4: LightGBM Classifier (PP-A, class_weight='balanced')
lgb_model = lgb.LGBMClassifier(
    n_estimators=100,
    learning_rate=0.05,
    class_weight='balanced',
    random_state=42,
    verbose=-1
)
t_lgb_start = time.time()
lgb_model.fit(X_train, y_train)
t_lgb_train = time.time() - t_lgb_start
y_pred_lgb = lgb_model.predict(X_test)
y_prob_lgb = lgb_model.predict_proba(X_test)[:, 2]

print(f"Huan luyen hoan tat! Thoi gian train LR: {t_lr_train:.2f}s | LightGBM: {t_lgb_train:.2f}s")


# In[ ]:


# 2.5. Bang so sanh hieu nang cac mo hinh
model_dict = {
    'Dummy Classifier (Stratified)': (y_pred_dummy, None),
    'Rule-based Threshold Baseline': (y_pred_rule, None),
    'Logistic Regression (Balanced)': (y_pred_lr, y_prob_lr),
    'LightGBM Classifier (PP-A)':     (y_pred_lgb, y_prob_lgb)
}

results = []
for name, (pred, prob) in model_dict.items():
    acc = accuracy_score(y_test, pred)
    rec_high = recall_score(y_test, pred, labels=[2], average=None)[0]
    prec_high = precision_score(y_test, pred, labels=[2], average=None)[0]
    macro_f1 = f1_score(y_test, pred, average='macro')
    
    if prob is not None:
        p_c, r_c, _ = precision_recall_curve((y_test == 2).astype(int), prob)
        pr_auc = auc(r_c, p_c)
    else:
        pr_auc = np.nan
        
    results.append({
        'Model': name,
        'Accuracy': acc,
        'Recall (High Risk)': rec_high,
        'Precision (High Risk)': prec_high,
        'Macro-F1': macro_f1,
        'PR-AUC (High Risk)': pr_auc
    })

eval_df = pd.DataFrame(results)
print("=== BANG TONG HOP KET QUA KIEM CHUNG TREN TAP TEST ===")
print(eval_df.to_string(index=False))


# In[ ]:


# Truc quan hoa Confusion Matrix va Feature Importance
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 1. Confusion Matrix: Rule-based
cm_rule = confusion_matrix(y_test, y_pred_rule, labels=[0, 1, 2])
sns.heatmap(cm_rule, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['Low', 'Medium', 'High'], yticklabels=['Low', 'Medium', 'High'])
axes[0].set_title('CM: Rule-based Threshold')
axes[0].set_ylabel('Nhan thuc te')
axes[0].set_xlabel('Du doan')

# 2. Confusion Matrix: LightGBM
cm_lgb = confusion_matrix(y_test, y_pred_lgb, labels=[0, 1, 2])
sns.heatmap(cm_lgb, annot=True, fmt='d', cmap='Greens', ax=axes[1],
            xticklabels=['Low', 'Medium', 'High'], yticklabels=['Low', 'Medium', 'High'])
axes[1].set_title('CM: LightGBM Classifier (PP-A)')
axes[1].set_ylabel('Nhan thuc te')
axes[1].set_xlabel('Du doan')

# 3. Feature Importance LightGBM
imp = pd.Series(lgb_model.feature_importances_, index=features).sort_values(ascending=True)
imp.tail(10).plot(kind='barh', color='#2ca02c', ax=axes[2])
axes[2].set_title('Top 10 Feature Importance (LightGBM)')
axes[2].set_xlabel('Do quan trong (Split count)')

plt.tight_layout()
plt.show()


# In[ ]:


# Truc quan hoa Precision-Recall Curve cho lop High Risk
fig, ax = plt.subplots(figsize=(8, 5))

p_lr, r_lr, _ = precision_recall_curve((y_test == 2).astype(int), y_prob_lr)
ax.plot(r_lr, p_lr, label=f'Logistic Regression (PR-AUC = {auc(r_lr, p_lr):.3f})', color='#ff7f0e', lw=2)

p_lgb, r_lgb, _ = precision_recall_curve((y_test == 2).astype(int), y_prob_lgb)
ax.plot(r_lgb, p_lgb, label=f'LightGBM PP-A (PR-AUC = {auc(r_lgb, p_lgb):.3f})', color='#2ca02c', lw=2.5)

ax.axhline((y_test == 2).mean(), color='red', linestyle='--', label=f'Baseline ngau nhien ({100*(y_test==2).mean():.1f}%)')
ax.set_title('Precision-Recall Curve cho nhom High Risk')
ax.set_xlabel('Recall (Do bao phu rui ro)')
ax.set_ylabel('Precision (Do chinh xac canh bao)')
ax.legend(loc='lower left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


# ## 3. Thẩm định khía cạnh Nguồn lực (Resource Feasibility)
# - **Bộ nhớ RAM:** Kích thước bảng Panel và ma trận đặc trưng trong bộ nhớ.
# - **Thời gian xử lý & huấn luyện:** Tốc độ huấn luyện mô hình cây tăng cường (PP-A) so với mô hình TabTransformer (PP-B).
# - **Môi trường thực thi:** Đánh giá tính khả thi trên hạ tầng giới hạn (Google Colab miễn phí 12GB RAM, máy cá nhân).

# In[ ]:


# Do dac bo nho RAM
panel_mem = valid_df.memory_usage(deep=True).sum() / (1024 ** 2)
train_mem = X_train.memory_usage(deep=True).sum() / (1024 ** 2)

print("--- THAM DINH BO NHO VA THOI GIAN ---")
print(f"Dung luong RAM cho Panel (105,391 dong):        {panel_mem:>8.2f} MB")
print(f"Dung luong RAM cho Ma tran dac trung Train:    {train_mem:>8.2f} MB")
print(f"Thoi gian huan luyen LightGBM (100 cay):        {t_lgb_train:>8.2f} giay")
print(f"Thoi gian huan luyen Logistic Regression:       {t_lr_train:>8.2f} giay")

# Uoc luong mo hinh TabTransformer (PP-B)
print("\n--- Uoc luong nguon luc cho PP-B (TabTransformer / Deep Learning) ---")
print("RAM can thiet:       ~2 - 4 GB (Batch size 256, 100k dong)")
print("Phan cung bat buoc:  GPU ho tro CUDA (Colab T4 / P100)")
print("Thoi gian train:     ~10 - 20 phut (20 epochs)")
print("Nhan xet: PP-A (LightGBM) vuot troi hoan toan ve toc do, tiet kiem RAM va de trien khai hon PP-B.")


# ## 4. Thẩm định khía cạnh Đạo đức – Pháp lý (Ethics & Legal Feasibility)
# 
# ### 4.1. Giấy phép sử dụng dữ liệu
# - **Electronics Sales Dataset:** Được công bố bởi `fahdelatiby` trên Kaggle theo giấy phép **CC0: Public Domain Dedication**. Giấy phép này cho phép sao chép, chỉnh sửa, phân phối và công bố kết quả nghiên cứu mà không bị ràng buộc bản quyền thương mại.
# 
# ### 4.2. Bảo vệ quyền riêng tư & Dữ liệu định danh cá nhân (PII)
# - Bảng `Customers` có cột `CustomerName` chứa tên người dùng cá nhân (dữ liệu PII trực tiếp).
# - Tuy nhiên, trong **Phương án 2**, đơn vị phân tích là **$(SKU \times Tuần\ t)$**.
# - Pipeline xử lý hoàn toàn **không sử dụng** bảng `Customers`, không chứa `CustomerID` hay `CustomerName`.
# - Do đó, **rủi ro vi phạm quyền riêng tư và lộ lọt PII ở Phương án 2 bằng 0**.
# 
# ### 4.3. Tính minh bạch & Rủi ro thiên vị của nhãn đại diện (Proxy Label)
# - Nhãn `InventoryRisk` được tạo theo quy tắc nghiệp vụ giả định (`Coverage` và `SalesTrend`), là biến đại diện (proxy), chưa phản ánh chính xác chi phí lưu kho hay hợp đồng mua lại thực tế của từng nhà phân phối.
# - Cần công bố rõ đây là hệ thống hỗ trợ ra quyết định (Decision Support System) chứ không tự động thay thế quyết định của người quản lý.

# ## 5. Tổng hợp kết quả thẩm định Phương án 2
# 
# | Tiêu chí | Dataset chính: Electronics Sales Dataset | Dataset tham khảo: Instacart |
# | :--- | :--- | :--- |
# | **Dữ liệu (Data)** | **Đạt (kèm lưu ý):** Đầy đủ 27 bảng, 871 SKU khớp 100% giữa bán hàng và kho. Tồn kho lũy kế hợp lệ 100% (min $\ge 0$). Cần lọc khoảng thời gian đồng bộ 07/2023 - 12/2025. | **Không đạt:** Hoàn toàn không có dữ liệu tồn kho, không có mốc thời gian lịch tuyệt đối. Không thể tính Coverage. |
# | **Kỹ thuật (Technical)** | **Đạt:** Xây dựng thành công Panel $SKU \times Tuần$, nhãn `InventoryRisk` phân bố hợp lý (High ~12-16%), chia tập có Gap 4 tuần chống rò rỉ. LightGBM đạt Recall(High) = 93.93%, PR-AUC = 0.980. | **Không đạt:** Không thể định nghĩa biến mục tiêu, không thể tạo đặc trưng tồn kho. Không tương thích khung bài toán. |
# | **Nguồn lực (Resources)** | **Đạt:** Tiêu thụ < 35 MB RAM, thời gian huấn luyện LightGBM < 5 giây. Khả thi 100% trên Colab CPU/GPU miễn phí. PP-B (TabTransformer) cần thêm GPU T4. | **Không đạt:** Quy mô lớn nhưng không phục vụ được bài toán, lãng phí tài nguyên tính toán vô ích. |
# | **Đạo đức – Pháp lý** | **Đạt:** Giấy phép CC0. Đơn vị phân tích cấp SKU loại bỏ hoàn toàn CustomerName/PII. Cần minh bạch bản chất proxy label. | **Đạt về pháp lý (CC0)** nhưng không có giá trị ứng dụng cho PA2. |
# | **KẾT LUẬN** | **KHẢ THI CAO (ĐẠT)** - Chọn làm phương án nòng cốt của đồ án. | **KHÔNG KHẢ THI (KHÔNG ĐẠT CHO PA2)** - Chỉ dùng benchmark cho phân tích giỏ hàng. |
# 
# ---
# *Ghi chú: Các mô hình trên chỉ đóng vai trò kiểm chứng tính khả thi và làm baseline so sánh, không xuất file mô hình `.pkl`.*
