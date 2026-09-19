# DS317 - Đồ án môn học: Khai Phá Dữ Liệu Trong Doanh Nghiệp

**Đề tài:** Phân tích & khai phá dữ liệu bán lẻ điện máy - Phân khúc khách hàng,
Dự đoán trả hàng, Dự báo doanh thu và Phân tích giỏ hàng.

**Bộ dữ liệu:** [Electronics Sales Dataset (B.Tech style)](https://www.kaggle.com/datasets/fahdelatiby/electronics-sales-dataset-b-tech-style) - Kaggle
(26 bảng dữ liệu quan hệ mô phỏng hệ thống bán lẻ điện máy).

---

## 📁 Cấu trúc thư mục

```
project/
├── data/
│   ├── raw/                  # 26 file CSV dữ liệu gốc (tải từ Kaggle)
│   └── processed/            # Dữ liệu đã làm sạch + kết quả trung gian
│       ├── sales_fact.parquet          # Bảng fact chính (578,425 dòng, 53 cột)
│       ├── customer_segments.csv       # Kết quả phân cụm RFM
│       ├── association_rules_*.csv     # Luật kết hợp tìm được
│       └── *_comparison.csv            # Bảng so sánh hiệu năng các mô hình
├── src/                       # Source code (chạy độc lập từng bước)
│   ├── preprocessing.py       # Tích hợp 26 bảng, làm sạch dữ liệu
│   ├── eda.py                 # Khám phá dữ liệu, sinh 15 biểu đồ
│   ├── customer_segmentation.py  # Bài toán 1: Phân cụm (RFM + K-Means)
│   ├── return_prediction.py      # Bài toán 2: Phân loại (dự đoán trả hàng)
│   ├── sales_forecasting.py      # Bài toán 3: Hồi quy & dự báo chuỗi thời gian
│   └── market_basket.py          # Bài toán 4: Luật kết hợp (giỏ hàng)
├── notebooks/
│   ├── DS317_DoAn_KhaiPhaDuLieu_executed.ipynb  # Notebook ĐÃ CHẠY, đầy đủ kết quả
│   ├── DS317_DoAn_KhaiPhaDuLieu.html            # Bản xem trực tiếp (không cần Jupyter)
│   └── DS317_DoAn_KhaiPhaDuLieu.py              # Bản nguồn dạng jupytext (dễ đọc diff)
├── outputs/
│   ├── figures/                # 29 biểu đồ trực quan hoá (.png)
│   ├── models/                 # Mô hình đã huấn luyện (.pkl)
│   └── reports/
│       ├── DS317_BaoCao_DoAn.docx   # Báo cáo Word hoàn chỉnh (26 trang)
│       └── DS317_BaoCao_DoAn.pdf    # Bản PDF tương ứng
├── report_build/               # Source code Node.js tạo báo cáo Word (docx-js)
├── requirements.txt
└── README.md
```

## 🚀 Cách chạy lại toàn bộ pipeline

```bash
pip install -r requirements.txt

cd src
python preprocessing.py           # Bước 1: tiền xử lý (~15s)
python eda.py                     # Bước 2: khám phá dữ liệu (~20s)
python customer_segmentation.py   # Bước 3: phân cụm khách hàng (~20s)
python return_prediction.py       # Bước 4: dự đoán trả hàng (~60s)
python sales_forecasting.py       # Bước 5: dự báo doanh thu (~140s)
python market_basket.py           # Bước 6: luật kết hợp (~20s)
```

Hoặc đơn giản nhất: **mở trực tiếp `notebooks/DS317_DoAn_KhaiPhaDuLieu.html`**
bằng trình duyệt để xem toàn bộ quy trình đã chạy sẵn - không cần cài đặt gì.

## 📊 Tóm tắt kết quả 4 bài toán khai phá dữ liệu

| Bài toán | Kỹ thuật | Kết quả chính |
|---|---|---|
| Phân khúc khách hàng | K-Means (RFM) | 3 phân khúc rõ rệt, Silhouette ≈ 0.40 |
| Dự đoán trả hàng | Random Forest / Logistic / GBM | AUC ≈ 0.55 - phát hiện: trả hàng gần như độc lập với đặc trưng đơn hàng |
| Dự báo doanh thu tháng | Random Forest (lag features) | MAPE ≈ 9.1% |
| Hồi quy giá trị đơn hàng | Hist Gradient Boosting | R² ≈ 0.77 |
| Luật kết hợp giỏ hàng | Apriori | 168 luật, lift cao nhất ≈ 17 (Desktop PCs-Keyboards) |

## 🔍 Các phát hiện chất lượng dữ liệu đáng chú ý

- **Dòng trùng lặp hoàn toàn**: SalesOrders (845), Customers (368), Shipments (371), CustomerReturns (25), Products (1) → đã loại bỏ.
- **Dữ liệu văn bản "bẩn"**: nhiều biến thể viết hoa/thường, khoảng trắng thừa cho cùng một giá trị (OrderStatus, FulfillmentMethod, AgeBand, ReturnOutcome) → đã chuẩn hoá.
- **Outlier thời gian**: 52 đơn hàng có ngày đặt hàng ngoài khung hoạt động thực tế (2023-07 → 2025-12) → đã loại bỏ.
- **Khách vãng lai**: ~28.7% đơn hàng không gắn với tài khoản khách hàng (mua trực tiếp không đăng ký) → gắn nhãn rõ ràng thay vì để trống/nhầm lẫn là lỗi.

Chi tiết đầy đủ xem tại `outputs/reports/DS317_BaoCao_DoAn.docx`.

## 📄 Giấy phép & nguồn dữ liệu

Dữ liệu gốc thuộc bản quyền của tác giả trên Kaggle, chỉ sử dụng cho mục đích học tập/nghiên cứu trong khuôn khổ môn học DS317.
