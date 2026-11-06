# Chốt hướng, điều kiện dữ liệu và kế hoạch sửa Colab

## 1. Định vị để hỏi giảng viên

Giữ một bài toán: dự báo giá giao dịch bình quân SKU của tuần t+1 từ thông tin đến cuối tuần t. Lịch sử ngắn/thưa là các điều kiện đánh giá cần định nghĩa và phân nhóm, không phải khẳng định toàn bộ Electronics là sparse, cũng không tự gọi là cold-start/few-shot. Gap là ứng viên trong các nguồn đã khảo sát, chưa phải tuyên bố novelty toàn literature.

Electronics đủ dùng làm pilot: 871 SKU, 130 tuần đầy đủ, 68.317 quan sát SKU–tuần; trung vị 81 tuần có giá và 699 SKU có ≥32 tuần quan sát. Last-price WAPE trên validation khoảng 1,086%; khoảng 30,22% nhãn validation đổi >1%, 7,12% đổi >5%. Có dữ liệu cho phân tích biến động nhưng baseline mạnh. Nguồn gốc thật/mô phỏng, giấy phép và tiền tệ chưa xác minh đầy đủ; không khẳng định hiệu quả kinh doanh thực tế.

## 2. Sửa notebook nào?

**Không ghi đè notebook cũ; tạo phiên bản mới để tránh nhầm artifact lượng bán/rủi ro với giá. Các tên bên dưới là đề xuất, chưa phải file notebook đã tạo/chạy.**

| Nguồn hiện có | Việc cần sửa | Notebook đích đề xuất |
| --- | --- | --- |
| BT Thuyết minh đề tài (Ver 1)-20261019T120039Z-1-001/BT Thuyết minh đề tài (Ver 1)/Lab3_DS317.R11_Nhom5_NB1_ES_BanHang.ipynb | Tái dùng load/schema/DQ/join và tổng hợp revenue/qty. Cell 22 đang forward-fill avg_price và dựng grid từ min–max bán toàn kỳ: tách observed_price khỏi last_price, không dùng ngày bán cuối tương lai quyết định cohort. Cell 24 đổi y_qty thành nhãn giá đúng tuần kế tiếp. Cell 26 cập nhật schema output. Các mục EDA 3.1–3.5 chuyển trọng tâm qty sang giá/biến động/coverage, bỏ phụ thuộc stock | NB01_Electronics_Price_DataAudit.ipynb |
| DS317_Lab3_Nhom5_NotebookChung.ipynb | Mục 4 không bắt buộc nạp tồn kho. Mục 5 modeling/split dùng giá và target_week, không risk/y_qty. Mục 6 phân phối giá/log-ratio/observation. Mục 7 thay baseline hai nhiệm vụ bằng last-price/rolling/Ridge/LightGBM. Mục 8 bỏ dual-head/multitask, thay bằng residual và ablation. Mục 9–10 bỏ cảnh báo rủi ro/ngưỡng lớp, thay bằng giá/thay đổi/recency/metrics. Cập nhật inventory/export/README cuối notebook | NB02_Electronics_Price_Pilot.ipynb |
| NB2 ES tồn kho, các notebook PA2 InventoryRisk | Lưu làm kết quả hướng cũ; không cần hoàn thiện để đủ điều kiện bài giá. Chỉ tái dùng feature tồn kho sau này nếu xác minh đúng thời điểm và có ablation; không bắt buộc | Không thuộc pipeline giá chính |
| Chưa có benchmark giá 10 model | Sau pilot tạo adapter, evaluator và chạy riêng env/checkpoint theo protocol SOTA; không chạy script dataset gốc rồi gọi đã chạy Electronics | NB03_Electronics_Price_Benchmark.ipynb |

Chỉ số cell là chỉ số 0-based trong JSON của NB1 đã đọc, không phải execution_count hiển thị trong Colab. Nhận diện bằng nội dung khi chỉnh vì số cell có thể thay đổi.

## 3. Hợp đồng dữ liệu mới

Giữ bảng quan sát SKU–tuần gồm sku_id, week_start, qty, revenue, observed_price, price_observed, discount_observed và biến danh mục đã kiểm tra. observed_price=revenue/qty chỉ có khi qty>0. last_price và recency lấy từ quá khứ, không điền ngược. Khoảng đầu lịch sử/padding phải có mask riêng.

Bảng modeling gồm sku_id, origin_week, target_week, last_price, recency_weeks, history_observation_count, coverage_L, features và y_price. target_week=origin_week+7 ngày; y_price lấy từ observed_price của đúng tuần đích bằng join hoặc shift trên lưới tuần đầy đủ. Không shift trên danh sách chỉ gồm tuần có giao dịch vì sẽ thành dự báo lần bán kế tiếp. Tuần đích không bán giữ nhãn missing; không drop origin ở đầu inference dựa trên tương lai.

Xuất sang thư mục phiên bản price_v1 riêng, không ghi đè mt_train/val/test của hướng cũ. Thêm split_metadata, quality_report và feature_availability với nguồn/công thức/cutoff cho mỗi feature. Cột chứa nhãn/giá trị tương lai nằm riêng, không auto-select tất cả numeric columns làm X.

## 4. Kiểm chứng tối thiểu trước khi nói hướng khả thi

1. Run all từ runtime Colab sạch; path/data setup tái lập; các bảng phía danh mục duy nhất, join cardinality đúng, không orphan không giải thích và không nhân tổng lượng/giá trị.
2. Assertion grid tuần, khóa SKU–origin duy nhất, nhãn đúng t+1, không target imputation/backfill; chặn FutureSales/cov_fwd/risk/y_qty khỏi X.
3. Chia theo target_week chung mọi SKU; preprocessing fit trên train. Giữ test để đánh giá cuối, không điều chỉnh phương pháp theo điểm test đã mở.
4. Đánh giá độ dài context 8/16/32 như limited-context study. Nếu model vẫn học nhiều lịch sử SKU trong train thì không gọi là few-shot trên SKU mới. Sparse tự nhiên phân nhóm theo lịch sử tại cutoff; nếu che quan sát nhân tạo phải giữ nguyên nhãn thật và ghi rõ missingness simulation, không coi giống cơ chế không bán thực tế.
5. Baseline last-price/rolling, Ridge, LightGBM raw và log-ratio; cùng prediction keys, có MAE/WAPE/macro-SKU, label coverage và lỗi chạy. Chưa bắt buộc chạy 10 model để gửi email xin ý kiến.
6. Nhóm stable/change dùng y sau khi quan sát chỉ để phân tích lỗi; chọn ngưỡng trên train và chốt trước test. Chỉ làm phân nhóm nếu đủ mẫu/SKU; báo số mẫu, không chọn nhóm theo gain đẹp.
7. Output minh họa gồm giá gần nhất, giá dự báo, % thay đổi, recency, coverage lịch sử và cờ đủ dữ liệu. Đây không phải xác suất rủi ro hay giá khuyến nghị tự động. Uncertainty chỉ thêm nếu có phương pháp/đánh giá phù hợp.

## 5. Mẫu email xin ý kiến

**Tiêu đề: [DS317.R11 – Nhóm 5] Xin góp ý định hướng dự báo giá bán thực tế theo SKU–tuần**

Kính gửi cô,

Sau khi trao đổi và rà soát lại phạm vi đề tài, nhóm em dự kiến tập trung vào một bài toán: dự báo giá bán thực tế bình quân gia quyền theo số lượng của từng SKU trong tuần kế tiếp, sử dụng thông tin có sẵn đến cuối tuần hiện tại. Nhóm không huấn luyện đồng thời nhiệm vụ phân loại rủi ro tồn kho.

Nhóm muốn đào sâu việc ảnh hưởng của độ dài lịch sử và mức độ quan sát giá đến kết quả dự báo. Với tuần không có giao dịch, nhóm xem giá thực tế là chưa quan sát, không tự điền làm nhãn; các biến ngoại sinh chỉ sử dụng khi có căn cứ sẵn có tại thời điểm dự báo. Nhóm sẽ đối sánh với baseline giữ nguyên giá gần nhất, đồng thời phân tích sai số trên các tuần giá ổn định và biến động. Đây là các điều kiện thực nghiệm trong cùng bài toán giá, chưa định vị thành cold-start/few-shot learning.

Về phần đã thực hiện, repo đã có notebook khảo sát, kiểm tra chất lượng và tổng hợp dữ liệu bán hàng theo SKU–tuần từ hướng cũ. Nhóm đã kiểm tra sơ bộ khả năng dùng bộ Electronics cho bài giá: có 871 SKU và 130 tuần đầy đủ; trên validation, baseline giá gần nhất có WAPE khoảng 1,09%. Trung vị mỗi SKU có 81 tuần quan sát nên nhóm không khẳng định toàn bộ dữ liệu đều ngắn/thưa. Nhóm dự kiến điều chỉnh notebook tạo nhãn và chia tập sang giá tuần kế tiếp, đồng thời bổ sung đặc trưng độ mới/độ phủ lịch sử. Pipeline huấn luyện giá và benchmark 10 mô hình chưa hoàn tất.

Về phương pháp, nhóm dự kiến thử học phần thay đổi giá tương đối quanh giá quan sát gần nhất, bổ sung thông tin mức độ quan sát và kiểm chứng bằng ablation. Nhóm đã khảo sát các phương pháp forecasting 2023–2026; phần còn cần kiểm chứng là hiệu quả trên giá giao dịch SKU–tuần trong điều kiện dữ liệu và thông tin đầu vào nêu trên, không khẳng định các mô hình hiện tại đều thiếu ngoại sinh hay xử lý missing.

Nhóm xin cô góp ý liệu phạm vi một bài toán với các phân tích trên có phù hợp học phần không, và bộ Electronics có thể dùng làm dữ liệu chính với giới hạn nguồn gốc dữ liệu được công bố rõ hay cần bổ sung bộ dữ liệu khác. Nhóm gửi kèm thuyết minh sơ bộ và bảng related work để cô tiện xem xét.

Nhóm em cảm ơn cô.

Trân trọng,
Đại diện Nhóm 5 – DS317.R11

**Lưu ý trước gửi:** xác nhận người nhận/cách xưng hô; mở lại file đính kèm; các con số là audit nội bộ, chưa phải kết quả model đề xuất. Email chưa được gửi tự động. Không mô tả 10 model đã chạy hoặc mô hình residual đã cải thiện khi chưa có log.