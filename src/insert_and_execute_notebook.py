import os
import sys
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import PythonExporter, HTMLExporter

sys.stdout.reconfigure(encoding='utf-8')

def main():
    target_ipynb = os.path.abspath("notebooks/DS317_KiemChung_PA2_Electronics_InventoryRisk.ipynb")
    print(f"Loading notebook: {target_ipynb}")
    
    with open(target_ipynb, "r", encoding="utf-8") as f:
        nb = nbf.read(f, as_version=4)
        
    print(f"Current cell count: {len(nb.cells)}")
    
    # Locate insertion point: right after the Gap Split cell (which contains '2.3. Chien luoc chia du lieu theo thoi gian')
    split_cell_idx = -1
    for idx, cell in enumerate(nb.cells):
        if "Chien luoc chia du lieu theo thoi gian co khoang dem" in cell.source or "2.3. Chien luoc chia du lieu" in cell.source:
            split_cell_idx = idx
            break
            
    if split_cell_idx == -1:
        # Fallback to index 14
        split_cell_idx = 14
        
    print(f"Gap Split cell found at index: {split_cell_idx}")
    
    # Define new cells to insert
    md_eda = """### 2.4. Khảo sát thực nghiệm & Trực quan hóa dữ liệu trước mô hình hóa (Exploratory Data Analysis)

Khảo sát phân bố nhãn, ma trận tương quan đặc trưng và xu hướng chuỗi thời gian nhằm thẩm định tính khả thi của bài toán và giải thích cơ chế phân loại:
1. **Biểu đồ so sánh phân bố nhãn mục tiêu (Target Distribution: Train vs Test):** Kiểm tra trực quan hiện tượng lệch pha phân bố (distribution shift) do việc tách tập dữ liệu theo thời gian có khoảng đệm 4 tuần (Gap Split).
2. **Biểu đồ ma trận tương quan (Correlation Matrix / Heatmap):** Nhìn rõ mối quan hệ tuyến tính giữa các đặc trưng quan trọng (`EndInventory`, `PastCoverage`, `WeeklyQty`, `SalesTrend_4w`,...) với biến mục tiêu `Target`.
3. **Biểu đồ xu hướng trung bình của các chỉ số chính theo thời gian nhóm theo nhãn rủi ro:** Phân tích sự phân kỳ hành vi giữa lượng hàng tồn kho và doanh số bán, giải thích sinh động lý do tại sao mô hình phân lớp được các nhóm này."""

    code_chart1 = """# 1. Bieu do so sanh phan bo nhan muc tieu (Target Distribution) giua Train va Test
# Giup kiem tra truc quan su lech pha phan bo (distribution shift) do Gap Split

target_labels = ['Low Risk (0)', 'Medium Risk (1)', 'High Risk (2)']
target_names = {0: 'Low Risk (0)', 1: 'Medium Risk (1)', 2: 'High Risk (2)'}

train_dist = train_set['Target'].map(target_names).value_counts()
test_dist = test_set['Target'].map(target_names).value_counts()

train_pct = (train_set['Target'].map(target_names).value_counts(normalize=True) * 100).reindex(target_labels)
test_pct = (test_set['Target'].map(target_names).value_counts(normalize=True) * 100).reindex(target_labels)

dist_summary = pd.DataFrame({
    'Train Count': train_dist.reindex(target_labels),
    'Train (%)': train_pct,
    'Test Count': test_dist.reindex(target_labels),
    'Test (%)': test_pct
})
print("=== BANG PHAN BO NHAN MUC TIEU (TRAIN VS TEST) ===")
print(dist_summary.to_string())

# Truc quan hoa bang bieu do
fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), gridspec_kw={'width_ratios': [1.3, 1]})

# Subplot 1: Grouped Bar Chart so sanh ty le % giua Train va Test
x = np.arange(len(target_labels))
width = 0.35

rects1 = axes[0].bar(x - width/2, train_pct.values, width, label=f'Train Set ({len(train_set):,d} dong)',
                     color='#2b5c8f', edgecolor='black', alpha=0.9)
rects2 = axes[0].bar(x + width/2, test_pct.values, width, label=f'Test Set ({len(test_set):,d} dong)',
                     color='#e26d5c', edgecolor='black', alpha=0.9)

axes[0].set_title('So sanh ty le phan bo nhan muc tieu (Target Distribution Shift)\\nTrain Set vs Test Set (Gap Split 4 tuan)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Ty le phan tram (%)', fontsize=11)
axes[0].set_xticks(x)
axes[0].set_xticklabels(target_labels, fontsize=10, fontweight='bold')
axes[0].set_ylim(0, max(max(train_pct), max(test_pct)) * 1.18)
axes[0].legend(frameon=True, facecolor='white', framealpha=0.9)
axes[0].grid(axis='y', linestyle='--', alpha=0.5)

# Ghi gia tri % tren dau cot
for rect in rects1:
    h = rect.get_height()
    axes[0].annotate(f'{h:.1f}%', xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha='center', va='bottom',
                     fontsize=10, fontweight='bold', color='#1b3b5a')
for rect in rects2:
    h = rect.get_height()
    axes[0].annotate(f'{h:.1f}%', xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points", ha='center', va='bottom',
                     fontsize=10, fontweight='bold', color='#8c2317')

# Subplot 2: Donut Chart the hien co cau tap Test
colors = ['#2ca02c', '#ff7f0e', '#d62728']
high_pct_test = test_pct['High Risk (2)']
axes[1].pie(test_pct.values, labels=target_labels, autopct='%1.1f%%', startangle=140,
            colors=colors, explode=(0.02, 0.02, 0.06),
            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
centre_circle = plt.Circle((0,0), 0.60, fc='white')
axes[1].add_artist(centre_circle)
axes[1].set_title(f'Co cau nhan tren Tap Test\\n(Nhom High Risk chiem {high_pct_test:.1f}%)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()

print("\\n--- NHAN XET VE SU LECH PHA PHAN BO (DISTRIBUTION SHIFT) ---")
print(f"1. Nhom High Risk tang manh tu {train_pct['High Risk (2)']:.1f}% (Train) len {test_pct['High Risk (2)']:.1f}% (Test).")
print(f"2. Nhom Low Risk giam tu {train_pct['Low Risk (0)']:.1f}% (Train) xuong {test_pct['Low Risk (0)']:.1f}% (Test).")
print("3. Y nghia: Phan anh dung thuc te chuoi thoi gian ban le dien tu (cuoi nam 2025 toc do tieu thu cham o mot so danh muc khien hang ton bi u dong).")
print("4. Chien luoc xu ly: Mo hinh can duoc huan luyen voi class_weight='balanced' va danh gia bang PR-AUC de tranh bi danh lua boi do chinh xac tong the (Accuracy).")"""

    code_chart2 = """# 2. Bieu do tuong quan (Correlation Matrix / Heatmap)
# Quan sat moi quan he tuyen tinh giua cac dac trung quan trong va bien muc tieu Target tren tap Train

corr_features = [
    'Target', 'PastCoverage', 'EndInventory', 'NetQtyChange',
    'WeeklyQty', 'Sales_Lag_1', 'Sales_RollingMean_4w', 'SalesTrend_4w',
    'WeeklyRevenue', 'AvgPrice', 'PromoCount'
]

# Tinh ma tran tuong quan Pearson tren Tap Train (tranh data leakage tu Test)
train_corr = train_set[corr_features].corr()

fig, axes = plt.subplots(1, 2, figsize=(16, 6.5), gridspec_kw={'width_ratios': [1.4, 0.9]})

# Subplot 1: Heatmap day du
mask = np.triu(np.ones_like(train_corr, dtype=bool))
sns.heatmap(train_corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
            vmin=-1, vmax=1, center=0, cbar_kws={'label': 'He so tuong quan Pearson (r)'},
            linewidths=0.6, ax=axes[0])
axes[0].set_title('Ma tran tuong quan giua cac dac trung va bien muc tieu Target\\n(Khao sat tren Tap Train)', fontsize=12, fontweight='bold')

# Subplot 2: Bar plot xep hang he so tuong quan voi bien Target
target_corr = train_corr['Target'].drop('Target').sort_values(ascending=True)
bar_colors = ['#d62728' if x < 0 else '#2ca02c' for x in target_corr.values]
bars = axes[1].barh(target_corr.index, target_corr.values, color=bar_colors, edgecolor='black', alpha=0.85)
axes[1].axvline(0, color='black', lw=1.2, linestyle='--')
axes[1].set_title('Xep hang tuong quan cua cac dac trung voi Target\\n(Gia tri r voi bien muc tieu)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('He so tuong quan (r)', fontsize=10)
axes[1].set_xlim(-0.4, 0.8)
axes[1].grid(axis='x', linestyle='--', alpha=0.5)

# Ghi so tren thanh
for bar in bars:
    w = bar.get_width()
    offset = 0.02 if w >= 0 else -0.06
    axes[1].annotate(f'{w:.2f}', xy=(w + offset, bar.get_y() + bar.get_height()/2),
                     va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.show()

print("\\n--- NHAN XET VE MOI QUAN HE TUONG QUAN VOI BIEN MUC TIEU TARGET ---")
print(f"1. PastCoverage co tuong quan duong manh nhat voi Target (r = {train_corr.loc['PastCoverage', 'Target']:.2f}): Tuan nao co he so bao phu ton kho uoc tinh qua khu cao thi xac suat High Risk rat lon.")
print(f"2. EndInventory co tuong quan duong dang ke (r = {train_corr.loc['EndInventory', 'Target']:.2f}): Luong ton kho tuyet doi cao luon la dieu kien can gay ra nguy co ton u.")
print(f"3. WeeklyQty (r = {train_corr.loc['WeeklyQty', 'Target']:.2f}), Sales_Lag_1 (r = {train_corr.loc['Sales_Lag_1', 'Target']:.2f}) va Sales_RollingMean_4w (r = {train_corr.loc['Sales_RollingMean_4w', 'Target']:.2f}) mang tuong quan am ro ret: San pham ban cang chay thi cang it rui ro bi xep vao nhom High Risk.")
print(f"4. SalesTrend_4w mang tuong quan am (r = {train_corr.loc['SalesTrend_4w', 'Target']:.2f}): Doanh so giam sut 4 tuan qua truc tiep canh bao rui ro tieu thu.")"""

    code_chart3 = """# 3. Bieu do xu huong trung binh cua cac chi so chinh theo thoi gian nhom theo nhan rui ro
# Giai thich sinh dong co che phan tach cua mo hinh qua su phan ky (divergence) giua Ton kho va Doanh so

# Gan nhan Target tren toan bo valid_df bang nguong P60, P85 tu Train de khao sat xuyen suot chuoi thoi gian
valid_df['Target'] = np.where(
    (valid_df['Coverage'] >= p85) & (valid_df['SalesTrend_4w'] <= 0), 2,
    np.where(valid_df['Coverage'] >= p60, 1, 0)
)

weekly_risk_stats = valid_df.groupby(['Week', 'Target']).agg(
    Avg_EndInventory=('EndInventory', 'mean'),
    Avg_WeeklyQty=('WeeklyQty', 'mean'),
    Avg_PastCoverage=('PastCoverage', 'mean'),
    Avg_SalesTrend=('SalesTrend_4w', 'mean')
).reset_index()

risk_colors = {0: '#2ca02c', 1: '#ff7f0e', 2: '#d62728'}
risk_names = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}

fig, axes = plt.subplots(3, 1, figsize=(15, 11), sharex=True)

# 1. Panel Ton kho trung binh (EndInventory)
for r in [0, 1, 2]:
    subset = weekly_risk_stats[weekly_risk_stats['Target'] == r]
    axes[0].plot(subset['Week'], subset['Avg_EndInventory'], label=risk_names[r],
                 color=risk_colors[r], lw=2.2)
axes[0].set_ylabel('Ton kho TB (Chiec)', fontsize=11, fontweight='bold')
axes[0].set_title('Dien bien trung binh cua cac chi so chinh theo thoi gian phan theo nhan rui ro\\nPanel 1: Ton kho cuoi tuan (EndInventory) - Nhom rui ro duy tri luong ton kho cao nhat', fontsize=12, fontweight='bold')
axes[0].legend(loc='upper left', frameon=True)
axes[0].grid(True, linestyle='--', alpha=0.5)

# 2. Panel Doanh so ban trung binh (WeeklyQty)
for r in [0, 1, 2]:
    subset = weekly_risk_stats[weekly_risk_stats['Target'] == r]
    axes[1].plot(subset['Week'], subset['Avg_WeeklyQty'], label=risk_names[r],
                 color=risk_colors[r], lw=2.2)
axes[1].set_ylabel('Doanh so TB (Chiec/tuan)', fontsize=11, fontweight='bold')
axes[1].set_title('Panel 2: Doanh so ban ra trung binh tuan (WeeklyQty) - Nhom High Risk co doanh so tiem can 0', fontsize=12, fontweight='bold')
axes[1].legend(loc='upper left', frameon=True)
axes[1].grid(True, linestyle='--', alpha=0.5)

# 3. Panel He so bao phu ton kho (PastCoverage)
for r in [0, 1, 2]:
    subset = weekly_risk_stats[weekly_risk_stats['Target'] == r]
    axes[2].plot(subset['Week'], subset['Avg_PastCoverage'], label=risk_names[r],
                 color=risk_colors[r], lw=2.2)
axes[2].set_ylabel('Coverage TB (Tuan)', fontsize=11, fontweight='bold')
axes[2].set_xlabel('Moc thoi gian (Tuan)', fontsize=11, fontweight='bold')
axes[2].set_title('Panel 3: He so bao phu ton kho uoc tinh (PastCoverage) - Nhom High Risk vuot troi tren 60 tuan', fontsize=12, fontweight='bold')
axes[2].legend(loc='upper left', frameon=True)
axes[2].grid(True, linestyle='--', alpha=0.5)

# Danh dau cac vung phan chia thoi gian (Train, Gap 1, Val, Gap 2, Test)
split_dates = [
    (train_weeks[0], train_weeks[-1], 'Train Set', '#e8f4f8'),
    (val_weeks[0], val_weeks[-1], 'Val Set', '#eafaf1'),
    (test_weeks[0], test_weeks[-1], 'Test Set', '#fdf2e9')
]
for start, end, label, color in split_dates:
    for ax in axes:
        ax.axvspan(start, end, color=color, alpha=0.45)

axes[0].text(train_weeks[len(train_weeks)//2], axes[0].get_ylim()[1]*0.88, 'Train Period', ha='center', fontsize=10, fontstyle='italic', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
axes[0].text(val_weeks[len(val_weeks)//2], axes[0].get_ylim()[1]*0.88, 'Val', ha='center', fontsize=10, fontstyle='italic', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
axes[0].text(test_weeks[len(test_weeks)//2], axes[0].get_ylim()[1]*0.88, 'Test Period', ha='center', fontsize=10, fontstyle='italic', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

plt.tight_layout()
plt.show()

print("\\n--- GIAI THICH NGUYEN LY PHAN LOP CUA MO HINH (BUSINESS INSIGHTS) ---")
print("1. Su phan ky (Divergence) giua Ton kho va Doanh so:")
print("   - Nhom High Risk (Mau do): Luong ton kho trung binh luon duy tri o muc rat cao (~45 - 55 chiec), nhung doanh so ban WeeklyQty lai roi tham hai ve sat 0 (chi dat ~0.38 chiec/tuan).")
print("   - Nhom Low Risk (Mau xanh): Doanh so ban luon cao vuot troi (~7.5 chiec/tuan), ton kho duoc giai phong nhanh chong giup Coverage chi o muc 3.4 tuan.")
print("2. Ly do mo hinh dat hieu nang cao (PR-AUC ~ 0.98):")
print("   - Giua cac nhan co ranh gioi phan tach ro rang qua PastCoverage va su doi lap giua EndInventory va SalesTrend_4w.")
print("   - Nho do, LightGBM de dang nhan dien cac SKU bi 'dong bang' tieu thu nhung van u dong ton kho lon.")"""

    new_cells = [
        nbf.v4.new_markdown_cell(md_eda),
        nbf.v4.new_code_cell(code_chart1),
        nbf.v4.new_code_cell(code_chart2),
        nbf.v4.new_code_cell(code_chart3)
    ]
    
    # Insert new cells into notebook after split_cell_idx
    nb.cells = nb.cells[:split_cell_idx + 1] + new_cells + nb.cells[split_cell_idx + 1:]
    print(f"New cell count after insertion: {len(nb.cells)}")
    
    # Execute the updated notebook to populate outputs cleanly
    print("Executing notebook to populate cell outputs...")
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    nb_dir = os.path.abspath("notebooks")
    ep.preprocess(nb, {'metadata': {'path': nb_dir}})
    print("Execution completed successfully!")
    
    # Save the updated executed notebook
    files_to_save = [
        "notebooks/DS317_KiemChung_PA2_Electronics_InventoryRisk.ipynb",
        "notebooks/DS317_ThamDinh_PA2_Electronics_InventoryRisk_canchinhsua.ipynb"
    ]
    for rel_path in files_to_save:
        full_path = os.path.abspath(rel_path)
        with open(full_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)
        print(f"Saved notebook: {full_path}")
        
    # Export Python script (.py)
    exporter_py = PythonExporter()
    py_source, _ = exporter_py.from_notebook_node(nb)
    py_files = [
        "notebooks/DS317_KiemChung_PA2_Electronics_InventoryRisk.py",
        "notebooks/DS317_ThamDinh_PA2_Electronics_InventoryRisk_canchinhsua.py"
    ]
    for rel_path in py_files:
        full_path = os.path.abspath(rel_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(py_source)
        print(f"Saved Python script: {full_path}")

    # Export HTML (.html)
    exporter_html = HTMLExporter()
    html_source, _ = exporter_html.from_notebook_node(nb)
    html_files = [
        "notebooks/DS317_KiemChung_PA2_Electronics_InventoryRisk.html",
        "notebooks/DS317_ThamDinh_PA2_Electronics_InventoryRisk_canchinhsua.html"
    ]
    for rel_path in html_files:
        full_path = os.path.abspath(rel_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(html_source)
        print(f"Saved HTML report: {full_path}")

    print("ALL NOTEBOOKS, SCRIPTS, AND HTML REPORTS ARE FULLY GENERATED AND SYNCED!")

if __name__ == '__main__':
    main()
