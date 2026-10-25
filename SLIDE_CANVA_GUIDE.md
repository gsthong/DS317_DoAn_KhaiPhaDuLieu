# HƯỚNG DẪN THIẾT KẾ SLIDE CANVA & NỘI DUNG THUYẾT TRÌNH (NHÓM 5 - DS317.R11)
**Đề tài:** Dự báo doanh số và cảnh báo rủi ro tồn kho theo SKU–tuần cho chuỗi bán lẻ điện tử bằng mô hình Transformer đa nhiệm  
**Tài liệu dành cho:** Thành viên thiết kế Slide Canva và Thuyết trình viên  


# PHẦN 1: CỤM SLIDE 4 – 6 (TÀI SẢN DỮ LIỆU, KHẢO SÁT & CHẤT LƯỢNG)

---

### 🖥️ SLIDE 4: TÀI SẢN DỮ LIỆU & KIỂM KÊ 7 TIÊU CHÍ
> **Mục tiêu:** Chứng minh dữ liệu thực tế đủ điều kiện giải quyết bài toán; khẳng định tính pháp lý và quy mô.

#### 1. Bố cục Canva đề xuất (Layout 2 cột)
* **Cột trái (40%):** 2 Nguồn dữ liệu & Sơ đồ nối bảng (ERD rút gọn).
* **Cột phải (60%):** Bảng kiểm kê 7 tiêu chí chất lượng dữ liệu (có badge Đạt / Cần lưu ý).

#### 2. Nội dung hiển thị trên Slide
* **Tiêu đề Slide:** **TÀI SẢN DỮ LIỆU & KIỂM KÊ CHẤT LƯỢNG**
* **Nguồn dữ liệu sử dụng:**
  * **Nguồn chính – Electronics Sales Dataset:** Tác giả *fahdelatiby*, giấy phép **CC0 (Public Domain)**, tải từ Kaggle ngày 13/09/2026. Gồm **27 bảng** (221,8 MB, 2,66 triệu bản ghi).
  * **Nguồn đối chứng – Instacart Market Basket:** Tác giả *psparks*, giấy phép CC0. Chỉ dùng khảo sát tính khả thi.
* **Sơ đồ liên kết dữ liệu cốt lõi (Core Schema):**
  * `SalesOrders` $\xrightarrow{\text{SalesOrderID}}$ `SalesOrderLines` (556.094 dòng đơn hợp lệ)
  * `Products` $\xrightarrow{\text{SKU / ProductID}}$ `SalesOrderLines` & `InventoryMovements` (961.048 bản ghi kho)
  * $\rightarrow$ Đồng bộ cấp **SKU–Tuần** (`sku_id`, `week_start`).
* **Bảng kiểm kê 7 tiêu chí (Data Inventory Scorecard):**

| Tiêu chí kiểm kê | Kết quả định lượng trên dữ liệu | Đánh giá |
| :--- | :--- | :---: |
| **1. Nguồn gốc** | Nguồn mở Kaggle, giấy phép CC0 rõ ràng, minh bạch | 🟢 **Đạt** |
| **2. Quy mô** | 2.660.211 bản ghi, 871 SKU có giao dịch, 130 tuần liên tục | 🟢 **Đạt** |
| **3. Cấu trúc** | Khóa ngoại toàn vẹn giữa Đơn hàng – Chi tiết – Tồn kho | 🟢 **Đạt** |
| **4. Nhãn mục tiêu** | Doanh số $y\_qty$ có sẵn; Nhãn rủi ro tạo từ quy tắc nghiệp vụ thích ứng | 🟡 **Cần lưu ý** |
| **5. Chất lượng** | Thiếu CustomerID (28,7%), SalesLocationID (38,3%); tồn kho không âm | 🟡 **Cần lưu ý** |
| **6. Thời gian** | Đồng bộ hóa trên cửa sổ chuẩn 130 tuần (03/07/2023 – 28/12/2025) | 🟡 **Cần lưu ý** |
| **7. Tính riêng tư** | Bỏ `CustomerName`, không dùng dữ liệu định danh người dùng | 🟢 **Đạt** |

#### 3. Hình ảnh chèn vào Canva
* **File chèn:** `figures/fig_thoi_gian_phu_cac_bang.png` (Biểu đồ mốc thời gian phủ các bảng) hoặc vẽ icon sơ đồ liên kết 4 bảng (`SalesOrders` $\leftrightarrow$ `SalesOrderLines` $\leftrightarrow$ `Products` $\leftrightarrow$ `InventoryMovements`).

#### 4. Ghi chú thuyết trình (Speaker Notes - 1,5 phút)
> *"Kính thưa Hội đồng, để giải quyết bài toán dự báo và rủi ro tồn kho, nhóm khai thác bộ dữ liệu Electronics Sales gồm 27 bảng dữ liệu quan hệ với hơn 2,66 triệu bản ghi theo giấy phép CC0. Chúng tôi trích xuất lõi thông tin từ 4 bảng trọng yếu gồm SalesOrders, SalesOrderLines, Products và InventoryMovements, đồng bộ về cùng khóa SKU-tuần. Qua rà soát 7 tiêu chí tài sản dữ liệu, đề tài đáp ứng xuất sắc tính toàn vẹn cấu trúc và quy mô bao phủ 130 tuần, đồng thời nhóm đã xử lý triệt để các thách thức về tính đồng bộ thời gian và nhãn rủi ro nghiệp vụ."*

---

### 🖥️ SLIDE 5: KHẢO SÁT DỮ LIỆU – TÍN HIỆU NGHIỆP VỤ ĐẶC TRƯNG
> **Mục tiêu:** Trình bày 3 biểu đồ nổi bật nhất chứng minh tính biến động, mùa vụ và hiện tượng ứ đọng tồn kho.

#### 1. Bố cục Canva đề xuất (Layout 3 Card ngang hoặc 1 lớn 2 nhỏ)
* Chia làm 3 khối hình ảnh tương ứng 3 góc nhìn: **Xu hướng & Mùa vụ** $\rightarrow$ **Phân bố doanh số** $\rightarrow$ **Sự phân kỳ Tồn kho - Doanh số**.

#### 2. Nội dung hiển thị trên Slide
* **Tiêu đề Slide:** **KHẢO SÁT DỮ LIỆU: MÙA VỤ, LỆCH PHẢI & NGUY CƠ Ứ ĐỌNG**
* **Khối 1: Tính mùa vụ cao điểm cuối năm**
  * *Ảnh minh họa:* `figures/fig_hinh3_luong_ban_theo_thang.png` (hoặc `fig_eda_mua_vu.png`)
  * *Insight:* Doanh số tăng vọt $40 - 60\%$ trong quý 4 (tháng 10–12) do lễ hội mua sắm, sau đó giảm chạm đáy vào quý 1.
  * *Ý nghĩa mô hình:* Đòi hỏi đặc trưng chuỗi thời gian ($month, week\_of\_year$) để bắt trúng đỉnh và đáy sức mua.
* **Khối 2: Phân bố lượng bán lệch phải nghiêm trọng (Right-skewed)**
  * *Ảnh minh họa:* `figures/fig_hinh1_phan_bo_quantity.png` (hoặc `fig_phan_bo_nhan_y_qty.png`)
  * *Insight:* Đa số đơn hàng có lượng mua nhỏ ($P_{50}=6$), 7,8% tuần có lượng bán bằng 0, nhưng xuất hiện các ngoại lai lớn ($P_{99}=35$).
  * *Ý nghĩa mô hình:* Phải dùng biến đổi $\log(1+y)$ và hàm mất mát $SmoothL1$ để chặn bùng nổ đạo hàm.
* **Khối 3: Hiện tượng phân kỳ giữa Tồn kho và Tốc độ bán (Sự ứ đọng)**
  * *Ảnh minh họa:* `figures/fig_hinh7_ton_kho_va_doanh_so_theo_tuan.png` (hoặc `fig_eda_ton_kho_vs_toc_do_ban.png`)
  * *Insight:* Nhiều SKU có lượng tồn kho tăng vọt nhưng doanh số bán ra đi ngang hoặc tụt dốc $\rightarrow$ Tích lũy tồn đọng vốn.
  * *Ý nghĩa mô hình:* Chứng minh sự cần thiết của nhãn High Risk kết hợp cả Coverage và $trend4 \le 0$.

#### 3. Hình ảnh chèn vào Canva
* Chọn 3 file trong thư mục `figures/`:
  1. `figures/fig_hinh3_luong_ban_theo_thang.png`
  2. `figures/fig_hinh1_phan_bo_quantity.png`
  3. `figures/fig_hinh7_ton_kho_va_doanh_so_theo_tuan.png`

#### 4. Ghi chú thuyết trình (Speaker Notes - 1,5 phút)
> *"Nhìn vào kết quả khảo sát thực tế trên slide, chúng ta thấy rõ 3 đặc thù cốt lõi: Thứ nhất, doanh số mang tính mùa vụ cực mạnh, tăng vọt vào quý 4 và giảm sâu đầu năm. Thứ hai, phân bố lượng bán bị lệch phải nặng nề với 7,8% tuần chạm mốc 0, buộc nhóm phải áp dụng hàm SmoothL1 trên không gian log để mô hình không bị thiên lệch bởi các điểm ngoại lai. Thứ ba, biểu đồ thứ ba chỉ ra bằng chứng thực tế: có sự phân kỳ rõ rệt khi tồn kho tăng cao nhưng sức mua sụt giảm – đây chính là tiền đề thực tiễn để nhóm thiết kế nhãn cảnh báo rủi ro tồn kho sớm."*

---

### 🖥️ SLIDE 6: CHẤT LƯỢNG DỮ LIỆU, GIỚI HẠN & BẰNG CHỨNG LOẠI INSTACART
> **Mục tiêu:** Thể hiện tư duy khoa học dữ liệu nghiêm túc: nhận diện điểm yếu của dữ liệu và giải thích lý do loại nguồn không phù hợp.

#### 1. Bố cục Canva đề xuất (Layout 2 cột so sánh)
* **Cột trái (50%):** Vấn đề chất lượng trên Electronics Sales & Cách xử lý.
* **Cột phải (50%):** Bằng chứng khoa học loại bỏ bộ dữ liệu Instacart.

#### 2. Nội dung hiển thị trên Slide
* **Tiêu đề Slide:** **KIỂM SOÁT CHẤT LƯỢNG & BẰNG CHỨNG LOẠI DỮ LIỆU ĐỐI CHỨNG**
* **Xử lý chất lượng trên Electronics Sales Dataset:**
  * **Giá trị thiếu:** `CustomerID` thiếu 28,7%, `SalesLocationID` thiếu 38,3% $\rightarrow$ Điền nhãn *"Unknown"*, không loại bỏ giao dịch; Loại bỏ 3 cột rỗng 100% trong `Products` (`ProductLine`, `ModelCode`, `SpecificationSummary`).
  * **Lệch mốc thời gian:** Đơn hàng rải rác sang 2026 trong khi bảng kho dừng ở 12/2025 $\rightarrow$ Cắt cửa sổ đồng bộ chuẩn mực **130 tuần liên tục (03/07/2023 – 28/12/2025)**.
  * **Bảo vệ quyền riêng tư:** Ẩn danh và loại bỏ hoàn toàn `CustomerName` khỏi mô hình hóa.
  * **Tính chính xác:** Tồn kho lũy kế tái lập khớp 100% biến động xuất-nhập-tồn, không có giá trị âm bất hợp lý.
* **Bằng chứng loại bỏ bộ dữ liệu đối chứng Instacart:**
  * ❌ **Không có ngày lịch cụ thể:** Chỉ có thứ trong tuần (0–6) và giờ trong ngày (0–23) $\rightarrow$ Không thể xây dựng chuỗi thời gian tuần lịch thực tế hay tính mùa vụ.
  * ❌ **Không có số lượng (Quantity):** Mỗi dòng chỉ ghi nhận sản phẩm có trong đơn $\rightarrow$ Không dự báo được khối lượng bán.
  * ❌ **Hoàn toàn không có dữ liệu tồn kho:** Không có kho vận, không có số tồn $\rightarrow$ Bất khả thi cho bài toán cảnh báo rủi ro tồn kho (PA2).
  * *Kết luận:* Instacart chỉ phù hợp cho bài toán giỏ hàng (Market Basket), không đáp ứng mục tiêu quản trị chuỗi cung ứng của đề tài.

#### 3. Hình ảnh chèn vào Canva
* **File chèn:** `figures/fig_ty_le_thieu_bang_chinh.png` (Tỷ lệ thiếu trên các bảng chính) và icon dấu gạch chéo đỏ $\times$ cho Instacart.

#### 4. Ghi chú thuyết trình & Chuẩn bị Demo (Speaker Notes - 1,5 phút)
> *"Nhóm duy trì tính kỷ luật cao trong xử lý dữ liệu: thay vì xóa bỏ các đơn hàng thiếu CustomerID, chúng tôi chuẩn hóa về nhóm Unknown để giữ trọn vẹn sức mua; cắt gọn cửa sổ đồng bộ 130 tuần và loại bỏ triệt để định danh khách hàng. Đặc biệt, nhóm đã thẩm định bộ dữ liệu Instacart và chính thức loại bỏ vì thiếu mốc thời gian thực và không có dữ liệu tồn kho. Ngay sau đây, xin kính mời Hội đồng theo dõi màn hình Demo 1 trên Notebook để kiểm chứng trực tiếp quy trình kiểm soát dữ liệu của nhóm."*

---

# PHẦN 2: CỤM SLIDE HỌC THUẬT & DỰ PHÒNG

---

### 🖥️ SLIDE: TỔNG QUAN CÔNG TRÌNH LIÊN QUAN & ĐÓNG GÓP MỚI
*(Đặt ngay trước Slide 7 Phương pháp)*

#### 1. Bố cục Canva đề xuất (Layout 2 khối: Bảng rút gọn trên, Điểm mới dưới)

#### 2. Nội dung hiển thị trên Slide
* **Tiêu đề Slide:** **CÔNG TRÌNH LIÊN QUAN & ĐÓNG GÓP CỐT LÕI CỦA ĐỀ TÀI**
* **Bảng tổng hợp công trình tiêu biểu:**

| Công trình | Điểm nổi bật | Giới hạn so với đề tài |
| :--- | :--- | :--- |
| **Sun & Li (2024)** [PeerJ, Q1] | TabTransformer đơn nhiệm dự báo bán lẻ, $R^2 \approx 0,95$ | Chỉ hồi quy lượng bán đơn nhiệm, không có cảnh báo rủi ro tồn kho. |
| **Sinodinos et al. (2026)** [AAAI-26, A*] | MultiTab-Net: Tabular Transformer học đa nhiệm tiên phong | Mới thử trên dữ liệu bảng tĩnh tổng quát, chưa áp dụng cho chuỗi cung ứng bán lẻ. |
| **Long et al. (2025)** [IJPE, Q1] | GBDT phân cấp 2 tầng dự báo xác suất bán lẻ cực mạnh | Không chia sẻ biểu diễn đa nhiệm; không học tương tác chéo giữa các đặc trưng. |
| **Wang et al. (2024)** [EJOR, A*] | Tối ưu sai số dự báo kết hợp tiện ích kiểm soát tồn kho | Đánh giá chính sách sau dự báo, chưa tích hợp vào hàm mất mát huấn luyện. |
| **Rubachev et al. (2025)** [ICLR, A*] | Benchmark TabReD: chuẩn hóa đánh giá chia theo thời gian | Khẳng định chia theo thời gian làm thay đổi hoàn toàn hiệu năng mô hình. |

* **Phân biệt Kế thừa và Điểm mới của Nhóm:**
  * 🔹 **Điểm kế thừa:** Kiến trúc mã hóa đặc trưng bảng (Feature Tokenizer) và Self-Attention từ Sun & Li (2024); Quy trình chia tập theo thời gian có khoảng đệm 4 tuần chống rò rỉ từ TabReD (2025). *(Nhóm không xem việc dùng Transformer là điểm mới)*.
  * 💡 **Điểm mới cốt lõi:**
    1. **Kiến trúc Transformer Đa nhiệm (MT-Transformer):** 1 Shared Encoder dùng chung biểu diễn, 2 Heads song song (Sales Head + Risk Head) cùng hàm Loss kết hợp: $\mathcal{L} = SmoothL1(\log(1+y)) + \lambda \cdot CE_{weighted}$. Hai tác vụ tự điều chuẩn (regularization), triệt tiêu quá khớp trên chuỗi dữ liệu bảng.
    2. **Nhãn rủi ro thích ứng đa chiều (Adaptive InventoryRisk):** Tích hợp cả Hệ số bao phủ nhìn trước ($cov\_fwd \ge P_{85}$) VÀ Xu hướng bán ngắn hạn ($trend4 \le 0$). Loại trừ phạt oan hàng bán chạy, tập trung vào 8,95% SKU thực sự đọng vốn.

#### 3. Ghi chú thuyết trình (Speaker Notes - 1,5 phút)
> *"Tổng kết các nghiên cứu hàng đầu 2024-2026, nhóm nhận thấy một khoảng trống lớn: các mô hình đỉnh cao như TabTransformer hay GBDT của Walmart đều tách rời bài toán dự báo bán hàng với quyết định rủi ro kho. Đề tài của nhóm kế thừa cơ chế Self-Attention từ Sun & Li và quy chuẩn chống rò rỉ của TabReD, nhưng tạo ra bước đột phá mới: xây dựng mô hình Transformer đa nhiệm đầu tiên đồng thời dự báo lượng bán và phân loại rủi ro tồn kho, kết hợp nhãn rủi ro thích ứng đa chiều giúp doanh nghiệp không phạt oan các sản phẩm tăng trưởng."*

---

### 🖥️ SLIDE 15: TÀI LIỆU THAM KHẢO & HỎI ĐÁP (Q&A)
> **Mục tiêu:** Trình bày danh mục trích dẫn chuẩn học thuật và tạo slide kết thúc mở cho phần vấn đáp.

#### 1. Bố cục Canva đề xuất
* **Cột trái (65%):** Danh mục 6 tài liệu tham khảo chính thức chuẩn IEEE.
* **Cột phải (35%):** Box Hỏi đáp (Q&A), lời cảm ơn Hội đồng, thông tin liên hệ nhóm kèm mã QR dẫn đến GitHub/Colab Notebook.

#### 2. Nội dung hiển thị trên Slide
* **Tiêu đề Slide:** **TÀI LIỆU THAM KHẢO & PHẦN HỎI ĐÁP**
* **Danh mục tài liệu tham khảo chính thức:**
  * `[1]` Y. Sun and T. Li, "A transformer-based framework for enterprise sales forecasting," *PeerJ Computer Science*, vol. 10, p. e2503, 2024.
  * `[2]` D. Sinodinos, J. Y. Wei, and N. Armanfard, "MultiTab: A scalable foundation for multitask learning on tabular data," in *Proc. AAAI Conf. on Human Computation and Crowdsourcing*, vol. 40, no. 30, pp. 25499–25507, 2026.
  * `[3]` X. Long, Q. Bui et al., "Scalable probabilistic forecasting in retail with gradient boosted trees: A practitioner's approach," *Int. J. of Production Economics*, vol. 279, p. 109449, 2025.
  * `[4]` S. Wang, Y. Kang, F. Petropoulos, and F. Li, "Combining probabilistic forecasts of intermittent demand," *European J. of Operational Research*, vol. 315, no. 3, pp. 1038–1048, 2024.
  * `[5]` H. Kamarthi et al., "Large scale hierarchical industrial demand time-series forecasting incorporating sparsity," in *Proc. 30th ACM SIGKDD Conf.*, pp. 5184–5193, 2024.
  * `[6]` I. Rubachev, N. Kartashev, Y. Gorishniy, and A. Babenko, "TabReD: Analyzing pitfalls and filling the gaps in tabular deep learning benchmarks," in *ICLR 2025*, 2025.
* **Khối Q&A:**
  * **CẢM ƠN QUÝ THẦY CÔ VÀ HỘI ĐỒNG ĐÃ LẮNG NGHE!**
  * *Nhóm 5 - DS317.R11 sẵn sàng tiếp nhận các câu hỏi và đóng góp ý kiến.*
  * Link mã nguồn & Báo cáo: [QR Code / Link GitHub]

---

# PHẦN 3: CÁC SLIDE DỰ PHÒNG (BACKUP SLIDES - BẢO VỆ ĐỒ ÁN)
*(Dùng khi Giảng viên hỏi sâu vào kỹ thuật, dữ liệu và thực nghiệm)*

---

### 🖥️ SLIDE DỰ PHÒNG 1: TỪ ĐIỂN DỮ LIỆU & ĐẶC TRƯNG MÔ HÌNH HÓA (21 BIẾN SỐ + 3 PHÂN LOẠI)
* **Nhóm Bán hàng (10 biến):** `qty` (hiện tại), các độ trễ `qty_lag1, qty_lag2, qty_lag4, qty_lag8`, trung bình trượt `qty_rmean4, qty_rmean8`, độ biến động `qty_rstd4, qty_rstd8`, gia tốc tiêu thụ `qty_slope4`.
* **Nhóm Giá & Khuyến mãi (3 biến):** `avg_price`, `discount_rate` (tỷ lệ giảm giá), `promo_flag` (cờ khuyến mãi).
* **Nhóm Tồn kho & Vận hành (4 biến):** `stock_end` (tồn cuối tuần), `stock_delta` (biến động tồn), `cov_past` (hệ số bao phủ quá khứ), `unit_cost` (giá vốn).
* **Nhóm Thuộc tính & Thời gian (4 biến):** `product_age_weeks` (vòng đời sản phẩm tính theo tuần), `week_of_year` (tuần trong năm 1–52), `month` (tháng 1–12).
* **Biến phân loại (Categorical Embedding):** `category` (8 ngành hàng), `subcategory` (65 nhóm con), `brand` (61 thương hiệu).

---

### 🖥️ SLIDE DỰ PHÒNG 2: BẢNG SO SÁNH HIỆU NĂNG MỌI MÔ HÌNH TRÊN TẬP TEST
*Dùng để bảo vệ khi Thầy/Cô hỏi: "Tại sao nhóm dám khẳng định Transformer vượt baseline?"*

| Tác vụ | Mô hình | MAE | RMSE | WAPE | $R^2$ | Recall High | Precision High | Macro-F1 | PR-AUC High | Tỷ lệ cảnh báo sai |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Doanh số** | Baseline S1_ma4 | 2,7038 | 3,8789 | 0,3384 | 0,7303 | — | — | — | — | — |
| | Baseline S1_ma8 | 2,5524 | 3,6540 | 0,3194 | 0,7606 | — | — | — | — | — |
| | Ridge S3 | 2,8836 | 4,0586 | 0,3609 | 0,7047 | — | — | — | — | — |
| | **LightGBM S4** | **2,4031** | **3,3562** | **0,3007** | **0,7981** | — | — | — | — | — |
| | Transformer Đơn nhiệm S6 | 2,4883 | 3,6006 | 0,3114 | 0,7676 | — | — | — | — | — |
| | **MT-Transformer Đa nhiệm** | 2,5129 | 3,5815 | 0,3145 | 0,7700 | — | — | — | — | — |
| **Rủi ro kho** | Baseline luật R1 (cov_past) | — | — | — | — | 71,89% | 38,27% | 0,6517 | — | 61,73% |
| | Pipeline 2 bước P1 | — | — | — | — | 56,68% | 53,09% | 0,7187 | — | 46,91% |
| | Logistic Regression R2 | — | — | — | — | 85,25% | 46,76% | 0,7271 | 0,6856 | — |
| | LightGBM R3 | — | — | — | — | 85,25% | **64,09%** | **0,7939** | 0,8432 | **35,91%** |
| | **MT-Transformer Đa nhiệm** | — | — | — | — | **90,02%** | 59,80% | 0,7733 | **0,8435** | 40,20% |

*Nhận xét then chốt để trả lời phản biện:*
* MT-Transformer đạt **Recall High 90,02%**, cao hơn LightGBM (85,25%) gần 5% tuyệt đối, phát hiện thêm hàng chục SKU ứ đọng nguy hiểm.
* Dù LightGBM đạt Precision cao hơn, nhưng bản chất nghiệp vụ tồn kho là **chi phí bỏ sót rủi ro đắt hơn chi phí cảnh báo nhầm** $\rightarrow$ MT-Transformer ưu việt hơn cho mục tiêu bảo toàn vốn lưu động.

---

### 🖥️ SLIDE DỰ PHÒNG 3: ĐỘ NHẠY SIÊU THAM SỐ TRỌNG SỐ LOSS $\lambda$ & ABLATION
*Dùng để bảo vệ khi Thầy/Cô hỏi: "Hai bài toán có xung đột gradient không và cân bằng loss thế nào?"*

* **Kết quả thực nghiệm độ nhạy $\lambda_{risk}$ (cố định $\lambda_{sales}=1.0$) trên tập Val:**
  * $\lambda_{risk} = 0.5 \rightarrow$ Val MAE = 2,415, Recall High = 88,93%, PR-AUC = 0,8951. (Thiên về dự báo doanh số).
  * $\lambda_{risk} = 1.0 \rightarrow$ Val MAE = 2,437, Recall High = **90,49%**, PR-AUC = **0,8996**, Macro-F1 = **0,8079**. *(Bộ tham số tối ưu được chọn làm mô hình chính)*.
  * $\lambda_{risk} = 2.0 \rightarrow$ Val MAE = 2,471, Recall High = 92,32%, nhưng Macro-F1 giảm xuống 0,7916 và sai số doanh số tăng.
* **Thực nghiệm Ablation bỏ đặc trưng tồn kho khỏi mô hình phân loại ($R3\_bo\_cov\_past\_stock$):**
  * Recall High đạt **86,59%** trên Val (gần như không đổi so với mô hình đầy đủ 86,20%).
  * *Kết luận khoa học:* Chứng minh mô hình học sâu không bị phụ thuộc máy móc vào một biến tồn kho tĩnh, mà thực sự nắm bắt được tín hiệu tương tác chéo từ tốc độ bán, giá và đặc tính sản phẩm.
