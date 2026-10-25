import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon

# Create canvas with exact academic aspect ratio (matching Hình 6)
fig, ax = plt.subplots(figsize=(12, 17.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Use clean sans-serif font
plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['font.family'] = 'sans-serif'

# ==============================================================================
# HELPER FUNCTIONS TO BUILD "BLOCK-BLOCK" ACADEMIC CARDS (EXACT HÌNH 6 STYLE)
# ==============================================================================
def draw_card(x, y, w, h, bg_color, border_color, lw=1.2, radius=0.6, linestyle='-'):
    """Draw a smooth rounded card with crisp border"""
    box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                         facecolor=bg_color, edgecolor=border_color, linewidth=lw, linestyle=linestyle)
    ax.add_patch(box)
    return box

def draw_header_card(x, y, w, h, header_h, header_bg, header_title, body_bg, border_color, 
                     title_color="#FFFFFF", title_size=9.2, radius=0.6):
    """Draw a card with a solid colored header bar and content body (exact Hình 6 style)"""
    draw_card(x, y, w, h, body_bg, border_color, lw=1.3, radius=radius)
    header = FancyBboxPatch((x, y + h - header_h), w, header_h, 
                            boxstyle=f"round,pad=0,rounding_size={radius}",
                            facecolor=header_bg, edgecolor=border_color, linewidth=1.3)
    ax.add_patch(header)
    rect_fill = patches.Rectangle((x, y + h - header_h), w, header_h * 0.35, 
                                  facecolor=header_bg, edgecolor='none')
    ax.add_patch(rect_fill)
    ax.plot([x, x + w], [y + h - header_h, y + h - header_h], color=border_color, lw=1.3)
    ax.text(x + w / 2, y + h - header_h / 2, header_title,
            fontsize=title_size, fontweight='bold', ha='center', va='center', color=title_color)

# ==============================================================================
# MAIN FIGURE TITLE (EXACT TOP BANNER STYLE)
# ==============================================================================
ax.text(50, 98.4, "Hình 9 – Lưu đồ phương án dự phòng và quy trình kiểm soát mô hình", 
        fontsize=13.5, fontweight='bold', ha='center', va='center', color='#0F172A')

# ==============================================================================
# 1) KHỐI 1: Ô BẦU DỤC (START)
# ==============================================================================
# “Kết thúc huấn luyện MT-Transformer; kiểm tra trên Validation”
b1 = FancyBboxPatch((18.0, 90.0), 64.0, 5.8, boxstyle="round,pad=0,rounding_size=2.9",
                    facecolor="#E3F2FD", edgecolor="#1976D2", linewidth=2.0)
ax.add_patch(b1)
ax.text(50.0, 93.3, "Kết thúc huấn luyện MT-Transformer", fontsize=10.5, fontweight='bold', ha='center', va='center', color='#0D47A1')
ax.text(50.0, 91.5, "Kiểm tra kỹ thuật trên tập Validation (16 tuần, 7.785 mẫu SKU–tuần)", fontsize=8.6, ha='center', va='center', color='#1565C0')

# Arrow from Block 1 -> Block 2 (Diamond)
ax.annotate('', xy=(34.0, 81.5), xytext=(34.0, 90.0),
            arrowprops=dict(arrowstyle="-|>", color="#1976D2", lw=2.2, mutation_scale=16))

# ==============================================================================
# 2) KHỐI 2: HÌNH THOI & Ô CHÚ THÍCH (3 ĐIỀU KIỆN KÍCH HOẠT)
# ==============================================================================
# Diamond at center-left: Center (34.0, 75.0), Width = 26.0, Height = 12.0
diamond_pts = [[34.0, 81.0], [47.0, 75.0], [34.0, 69.0], [21.0, 75.0]]
diamond = patches.Polygon(diamond_pts, closed=True, facecolor="#FEF3C7", edgecolor="#D97706", linewidth=2.2)
ax.add_patch(diamond)
ax.text(34.0, 76.4, "Xảy ra ≥ 1", fontsize=9.6, fontweight='bold', ha='center', va='center', color='#92400E')
ax.text(34.0, 74.8, "điều kiện kích hoạt", fontsize=9.2, fontweight='bold', ha='center', va='center', color='#92400E')
ax.text(34.0, 73.2, "dự phòng?", fontsize=9.6, fontweight='bold', ha='center', va='center', color='#92400E')

# Dashed connection line from Diamond (47.0, 75.0) to Callout box (52.0, 75.0)
ax.plot([47.0, 52.0], [75.0, 75.0], color="#D97706", linestyle=":", lw=2.0)

# Ô CHÚ THÍCH NỐI VÀO HÌNH THOI (BLOCK CARD THEO PHONG CÁCH HÌNH 6)
callout_x, callout_y, callout_w, callout_h = 52.0, 66.5, 43.5, 17.0
draw_header_card(callout_x, callout_y, callout_w, callout_h, 3.0, "#D97706", 
                 "3 ĐIỀU KIỆN KÍCH HOẠT DỰ PHÒNG", "#FFFBEB", "#F59E0B", title_size=8.5, radius=0.6)

txt_cond1 = "• (a) Không đạt ngưỡng chấp nhận:"
txt_cond1_sub = "  - MAE_val > 2,72 (tệ hơn MA4 quá 5%)\n  - HOẶC Recall High_val < 85% (bỏ sót rủi ro)"

txt_cond2 = "• (b) Quá tải / Lỗi tính toán:"
txt_cond2_sub = "  - Lỗi GPU / Out-Of-Memory (OOM)\n  - HOẶC huấn luyện > 15 phút không hội tụ"

txt_cond3 = "• (c) Xung đột đa nhiệm (Negative Transfer):"
txt_cond3_sub = "  - 1 nhánh suy giảm > 10% so với đơn nhiệm (S6 / R4)"

ax.text(53.5, 78.5, txt_cond1, fontsize=7.6, fontweight='bold', ha='left', va='center', color='#B45309')
ax.text(53.5, 76.5, txt_cond1_sub, fontsize=7.2, ha='left', va='center', color='#334155')

ax.text(53.5, 73.8, txt_cond2, fontsize=7.6, fontweight='bold', ha='left', va='center', color='#B45309')
ax.text(53.5, 71.8, txt_cond2_sub, fontsize=7.2, ha='left', va='center', color='#334155')

ax.text(53.5, 69.2, txt_cond3, fontsize=7.6, fontweight='bold', ha='left', va='center', color='#B45309')
ax.text(53.5, 67.5, txt_cond3_sub, fontsize=7.2, ha='left', va='center', color='#334155')

# ==============================================================================
# RẼ NHÁNH: "KHÔNG" (BÊN TRÁI) vs "CÓ" (BÊN PHẢI) - ĐÈ TRỰC TIẾP LÊN MŨI TÊN (-->)
# ==============================================================================
# 1. NHÁNH KHÔNG (MÀU XANH LÁ): từ đỉnh trái diamond (21.0, 75.0) -> sang trái 14.0 -> đâm thẳng xuống Khối 3
# Đường mũi tên xanh
ax.plot([21.0, 14.0, 14.0], [75.0, 75.0, 58.0], color="#00897B", lw=2.4, zorder=2)
ax.annotate('', xy=(14.0, 57.5), xytext=(14.0, 59.0),
            arrowprops=dict(arrowstyle="-|>", color="#00897B", lw=2.4, mutation_scale=16), zorder=2)

# Badge "KHÔNG: Mô hình đạt chuẩn" ĐÈ TRỰC TIẾP LÊN MŨI TÊN XANH (tâm X=14.0, Y=66.5)
lbl_k_w, lbl_k_h = 18.2, 4.2
lbl_k_x, lbl_k_y = 14.0 - lbl_k_w / 2, 66.5 - lbl_k_h / 2
box_k = FancyBboxPatch((lbl_k_x, lbl_k_y), lbl_k_w, lbl_k_h, boxstyle="round,pad=0,rounding_size=0.5",
                       facecolor="#E8F8F5", edgecolor="#00897B", linewidth=1.6, zorder=4)
ax.add_patch(box_k)
ax.text(14.0, 67.4, "KHÔNG", fontsize=8.8, fontweight='bold', ha='center', va='center', color='#004D40', zorder=5)
ax.text(14.0, 65.6, "(Mô hình đạt chuẩn)", fontsize=7.4, fontweight='bold', ha='center', va='center', color='#00796B', zorder=5)

# 2. NHÁNH CÓ (MÀU ĐỎ): từ đỉnh dưới diamond (34.0, 69.0) -> thẳng xuống 60.5 -> sang phải 74.25 -> đâm xuống Khối 4
# Đường mũi tên đỏ
ax.plot([34.0, 34.0, 74.25, 74.25], [69.0, 60.5, 60.5, 58.0], color="#C0392B", lw=2.4, zorder=2)
# Mũi tên định hướng trên đoạn nằm ngang (từ trái sang phải)
ax.annotate('', xy=(56.0, 60.5), xytext=(53.0, 60.5),
            arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=2.0, mutation_scale=12), zorder=2)
# Đầu mũi tên đâm thẳng vào nóc Khối 4
ax.annotate('', xy=(74.25, 57.5), xytext=(74.25, 59.0),
            arrowprops=dict(arrowstyle="-|>", color="#C0392B", lw=2.4, mutation_scale=16), zorder=2)

# Badge "CÓ: Kích hoạt dự phòng" ĐÈ TRỰC TIẾP LÊN MŨI TÊN ĐỎ (tâm X=34.0, Y=65.0 ngay dưới đáy diamond)
lbl_c_w, lbl_c_h = 18.2, 4.2
lbl_c_x, lbl_c_y = 34.0 - lbl_c_w / 2, 65.0 - lbl_c_h / 2
box_c = FancyBboxPatch((lbl_c_x, lbl_c_y), lbl_c_w, lbl_c_h, boxstyle="round,pad=0,rounding_size=0.5",
                       facecolor="#FDEDEC", edgecolor="#C0392B", linewidth=1.6, zorder=4)
ax.add_patch(box_c)
ax.text(34.0, 65.9, "CÓ", fontsize=8.8, fontweight='bold', ha='center', va='center', color='#900C3F', zorder=5)
ax.text(34.0, 64.1, "(Kích hoạt dự phòng)", fontsize=7.4, fontweight='bold', ha='center', va='center', color='#C0392B', zorder=5)

# ==============================================================================
# 3) KHỐI 3: NHÁNH "KHÔNG" (BÊN TRÁI, VIỀN XANH LÁ)
# ==============================================================================
# Hình chữ nhật: “Triển khai mô hình chính: MT-Transformer đa nhiệm (1 lần suy luận cho cả doanh số và rủi ro)”
c3_x, c3_y, c3_w, c3_h = 4.5, 27.0, 42.0, 31.0
draw_card(c3_x, c3_y, c3_w, c3_h, "#E8F8F5", "#00897B", lw=1.8, radius=0.8)

# Header Bar (Solid Green)
draw_header_card(5.5, 52.0, 40.0, 5.0, 5.0, "#00897B", 
                 "Triển khai mô hình chính:\nMT-Transformer đa nhiệm", 
                 "#FFFFFF", "#00897B", title_size=9.0, radius=0.6)

# Sub-block 1: Cơ chế 1 lần suy luận
draw_card(6.0, 44.5, 39.0, 6.5, "#FFFFFF", "#80CBC4", lw=1.0, radius=0.5)
ax.text(7.0, 49.3, "Cơ chế 1 lần suy luận duy nhất:", fontsize=7.8, fontweight='bold', ha='left', va='center', color='#004D40')
ax.text(7.0, 47.4, "• Shared Transformer Encoder trích xuất vector ẩn h = [CLS]", fontsize=7.3, ha='left', va='center', color='#1E293B')
ax.text(7.0, 45.6, "• Rẽ nhánh đồng thời: Sales Head (ŷ) & Risk Head (P_High)", fontsize=7.3, ha='left', va='center', color='#1E293B')

# Sub-block 2: Gợi ý ghi chú số liệu cạnh khối 3 (theo đúng spec)
draw_card(6.0, 31.5, 39.0, 12.0, "#FFFFFF", "#80CBC4", lw=1.0, radius=0.5)
ax.text(7.0, 41.8, "Số liệu thực tế trên tập Test (3 seeds):", fontsize=7.8, fontweight='bold', ha='left', va='center', color='#004D40')
ax.text(7.0, 39.6, "• Hiện đạt: MAE ≈ 2,52 (2,5199 - thấp hơn MA4 6,8%)", fontsize=7.4, ha='left', va='center', color='#1E293B')
ax.text(7.0, 37.6, "• Recall High ≈ 89% (trung bình 89,15%, seed 42: 90,0%)", fontsize=7.4, fontweight='bold', ha='left', va='center', color='#00796B')
ax.text(7.0, 35.6, "• PR-AUC High ≈ 0,843 (+23% so với Logistic)", fontsize=7.4, ha='left', va='center', color='#1E293B')
ax.text(7.0, 33.6, "• Tỷ lệ cảnh báo sai: 40,2% (sát ngưỡng 40%)", fontsize=7.4, ha='left', va='center', color='#1E293B')
ax.text(7.0, 32.0, "-> Tiết kiệm 50% chi phí tính toán so với 2 mô hình rời", fontsize=7.0, fontstyle='italic', ha='left', va='center', color='#004D40')

# Status Badge inside Block 3
draw_card(9.5, 27.8, 32.0, 2.8, "#00897B", "#004D40", lw=1.0, radius=0.4)
ax.text(25.5, 29.2, "[ĐẠT CHUẨN] TRIỂN KHAI MÔ HÌNH CHÍNH", fontsize=7.5, fontweight='bold', ha='center', va='center', color='#FFFFFF')

# ==============================================================================
# 4) KHỐI 4: NHÁNH "CÓ" (BÊN PHẢI, VIỀN ĐỎ)
# ==============================================================================
# Hình chữ nhật “Kích hoạt phương án dự phòng”, tách làm 2 khối song song
c4_x, c4_y, c4_w, c4_h = 52.0, 27.0, 44.5, 31.0
draw_card(c4_x, c4_y, c4_w, c4_h, "#FDEDEC", "#C0392B", lw=1.8, radius=0.8)

# Header Bar (Solid Red)
draw_header_card(53.0, 52.0, 42.5, 5.0, 5.0, "#C0392B", 
                 "Kích hoạt phương án dự phòng\n(Hybrid GBDT Pipeline)", 
                 "#FFFFFF", "#C0392B", title_size=9.0, radius=0.6)

# 2 KHỐI SONG SONG BÊN TRONG KHỐI 4 (theo đúng yêu cầu spec)
# 4.1: Nhánh 1 – Doanh số: LightGBM S4 (hoặc MA4 S1)
draw_header_card(53.5, 37.5, 20.2, 13.5, 2.4, "#E74C3C", 
                 "Nhánh 1 – Doanh số", "#FFFFFF", "#FFCDD2", title_size=7.6, radius=0.5)
ax.text(63.6, 46.2, "LightGBM (S4)", fontsize=8.6, fontweight='bold', ha='center', va='center', color='#1E293B')
ax.text(63.6, 44.6, "(hoặc MA4 S1)", fontsize=6.8, fontstyle='italic', ha='center', va='center', color='#64748B')
ax.text(54.5, 42.2, "• MAE Test: 2,4031", fontsize=7.2, ha='left', va='center', color='#1E293B')
ax.text(54.5, 40.4, "• R²: 0,7981 | WAPE: 0,30", fontsize=7.2, ha='left', va='center', color='#1E293B')
ax.text(54.5, 38.6, "-> Dẫn đầu độ chính xác", fontsize=6.8, fontweight='bold', ha='left', va='center', color='#00796B')

# 4.2: Nhánh 2 – Rủi ro: LightGBM R3
draw_header_card(75.0, 37.5, 20.2, 13.5, 2.4, "#E74C3C", 
                 "Nhánh 2 – Rủi ro kho", "#FFFFFF", "#FFCDD2", title_size=7.6, radius=0.5)
ax.text(85.1, 46.2, "LightGBM (R3)", fontsize=8.6, fontweight='bold', ha='center', va='center', color='#1E293B')
ax.text(85.1, 44.6, "(Phân loại 3 mức)", fontsize=6.8, fontstyle='italic', ha='center', va='center', color='#64748B')
ax.text(76.0, 42.2, "• Recall High: 85,25%", fontsize=7.2, ha='left', va='center', color='#1E293B')
ax.text(76.0, 40.4, "• Cảnh báo sai: 35,91%", fontsize=7.2, fontweight='bold', ha='left', va='center', color='#00796B')
ax.text(76.0, 38.6, "-> Kiểm soát cảnh báo giả", fontsize=6.8, fontweight='bold', ha='left', va='center', color='#00796B')

# Ghi chú số liệu cạnh khối 4 (theo đúng spec)
draw_card(53.5, 31.5, 41.5, 5.0, "#FFFFFF", "#FFCDD2", lw=1.0, radius=0.5)
ax.text(54.5, 35.0, "Ghi chú số liệu LightGBM dự phòng:", fontsize=7.5, fontweight='bold', ha='left', va='center', color='#900C3F')
ax.text(54.5, 33.3, "• LightGBM: MAE 2,40 | Recall High 85,25% | Cảnh báo sai 35,91%", fontsize=7.1, ha='left', va='center', color='#334155')
ax.text(54.5, 32.0, "• Huấn luyện vài giây trên CPU, hoàn toàn không phụ thuộc GPU", fontsize=7.0, fontstyle='italic', ha='left', va='center', color='#64748B')

# Status Badge inside Block 4
draw_card(58.0, 27.8, 32.5, 2.8, "#C0392B", "#900C3F", lw=1.0, radius=0.4)
ax.text(74.25, 29.2, "[DỰ PHÒNG] SẴN SÀNG KÍCH HOẠT THAY THẾ", fontsize=7.5, fontweight='bold', ha='center', va='center', color='#FFFFFF')

# ==============================================================================
# 5) KHỐI 5: GỘP MŨI TÊN TỪ KHỐI 3 VÀ 4 VÀO KHỐI CUỐI
# ==============================================================================
# "Hai nhánh dự phòng gộp lại thành một mũi tên; cùng với mũi tên từ khối 3 đi vào khối cuối: Bảng điều khiển Top-K SKU rủi ro cao"

# Path from Block 3 (Left): (25.5, 27.0) -> down to 21.0 -> right to 50.0
ax.plot([25.5, 25.5, 50.0], [27.0, 21.0, 21.0], color="#00897B", lw=2.2)

# Path from Block 4 (Right): (74.25, 27.0) -> down to 21.0 -> left to 50.0 (1 đường duy nhất, đối xứng hoàn hảo)
ax.plot([74.25, 74.25, 50.0], [27.0, 21.0, 21.0], color="#C0392B", lw=2.2)

# Combined arrow down into Destination Block 5
ax.annotate('', xy=(50.0, 18.0), xytext=(50.0, 21.0),
            arrowprops=dict(arrowstyle="-|>", color="#1565C0", lw=2.6, mutation_scale=17))
ax.text(50.0, 21.0, "Đồng bộ chuẩn hóa đầu ra", fontsize=7.6, fontstyle='italic', ha='center', va='center', 
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#E3F2FD", edgecolor="#90CAF9", lw=0.8), color='#0D47A1')

# KHỐI 5 (DESTINATION): “Bảng điều khiển Top-K SKU rủi ro cao”
# Clean Block Style, Light Themed (Cyan/Blue)
c5_x, c5_y, c5_w, c5_h = 5.0, 4.5, 91.0, 13.2
draw_card(c5_x, c5_y, c5_w, c5_h, "#EBF5FB", "#85C1E9", lw=1.4, radius=0.8)

# Header Bar (Solid Blue)
draw_header_card(6.0, 14.5, 89.0, 3.0, 3.0, "#1565C0", 
                 "BẢNG ĐIỀU KHIỂN TOP-K SKU RỦI RO CAO (HỖ TRỢ RA QUYẾT ĐỊNH HẰNG TUẦN)", 
                 "#FFFFFF", "#1565C0", title_size=9.0, radius=0.5)

# Table Header row
table_y = 11.2
table_h = 2.8
draw_card(6.5, table_y, 88.0, table_h, "#D4E6F1", "#A9CCE3", lw=0.8, radius=0.4)
cols = [
    ("Mã SKU", 12.0),
    ("Tồn cuối tuần", 24.5),
    ("Doanh số dự báo ŷ", 39.5),
    ("Coverage dự báo", 54.0),
    ("Xác suất High", 68.0),
    ("Khuyến nghị nghiệp vụ", 84.5)
]
for title, cx in cols:
    ax.text(cx, table_y + table_h / 2, title, fontsize=7.5, fontweight='bold', ha='center', va='center', color='#1B4F72')

# Table Data row 1 (Demo SKU 1)
row1_y = 8.2
row_h = 2.6
draw_card(6.5, row1_y, 88.0, row_h, "#FFFFFF", "#BDC3C7", lw=0.8, radius=0.3)
row1_data = [
    ("SKU0000739", 12.0, '#1E293B', True),
    ("27 chiếc", 24.5, '#334155', False),
    ("0,55 chiếc/tuần", 39.5, '#334155', False),
    ("49,3 tuần (> P85)", 54.0, '#C0392B', True),
    ("0,996 (High Risk)", 68.0, '#C0392B', True),
    ("Khuyến mãi/giảm giá + Hoãn nhập", 84.5, '#D35400', True)
]
for val, cx, col, is_b in row1_data:
    ax.text(cx, row1_y + row_h / 2, val, fontsize=7.2, 
            fontweight='bold' if is_b else 'normal', ha='center', va='center', color=col)

# Table Data row 2 (Demo SKU 2)
row2_y = 5.2
draw_card(6.5, row2_y, 88.0, row_h, "#F8F9F9", "#BDC3C7", lw=0.8, radius=0.3)
row2_data = [
    ("SKU0000697", 12.0, '#1E293B', True),
    ("39 chiếc", 24.5, '#334155', False),
    ("0,97 chiếc/tuần", 39.5, '#334155', False),
    ("40,4 tuần (> P85)", 54.0, '#C0392B', True),
    ("0,995 (High Risk)", 68.0, '#C0392B', True),
    ("Khuyến mãi/giảm giá + Hoãn nhập", 84.5, '#D35400', True)
]
for val, cx, col, is_b in row2_data:
    ax.text(cx, row2_y + row_h / 2, val, fontsize=7.2, 
            fontweight='bold' if is_b else 'normal', ha='center', va='center', color=col)

# ==============================================================================
# FOOTER BAR (METADATA)
# ==============================================================================
draw_card(5.0, 0.8, 55.0, 3.2, "#F2F4F4", "#BDC3C7", lw=1.0, radius=0.4)
ax.text(6.5, 2.7, "[!] Tiêu chuẩn kích hoạt dự phòng:", fontsize=7.4, fontweight='bold', ha='left', va='center', color='#1A5276')
ax.text(6.5, 1.5, "MAE_val > 2,72 | Recall High_val < 85% | Train > 15 min | Suy giảm nhánh > 10%", 
        fontsize=6.8, ha='left', va='center', color='#34495E')

draw_card(62.0, 0.8, 34.0, 3.2, "#E8F8F5", "#A3E4D7", lw=1.0, radius=0.4)
ax.text(63.5, 2.7, "[*] Trạng thái thực tế:", fontsize=7.4, fontweight='bold', ha='left', va='center', color='#117A65')
ax.text(63.5, 1.5, "MT-Transformer đạt chuẩn -> Triển khai chính", 
        fontsize=6.8, fontweight='bold', ha='left', va='center', color='#0E6251')

plt.tight_layout()
output_path = 'd:/DS317_DoAn_KhaiPhaDuLieu/outputs/fig_hinh9_phuong_an_du_phong.png'
plt.savefig(output_path, bbox_inches='tight', dpi=300)
print('Figure 9 strictly following prompt specifications saved successfully!')
