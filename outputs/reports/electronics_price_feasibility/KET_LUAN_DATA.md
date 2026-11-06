# Thẩm định Electronics cho dự báo giá SKU–tuần

Ngày kiểm tra: 06/11/2026. Script nguồn: src/audit_electronics_price_feasibility.py. Không sửa raw data; không huấn luyện mô hình và không dùng điểm test để lựa chọn phương pháp. Kiểm tra này đánh giá tính khả thi nội bộ, chưa xác minh nguồn gốc thật/mô phỏng, giấy phép hoặc tiền tệ.

## 1. Kết luận

**Giữ Electronics làm dữ liệu pilot chính; chưa cần đổi ngay. Chưa đủ căn cứ khóa làm benchmark duy nhất cho tuyên bố cải tiến SOTA.** Dữ liệu đủ nhãn, liên kết bảng và độ dài cho bài dự báo một tuần. Vấn đề quan trọng hơn độ sạch là mức giá ổn định cao và khả năng model học được phần thay đổi ngoài baseline last-price.

Không định vị toàn bộ dataset là cold-start/few-shot hoặc rất thưa. Độ dài/thưa là phân nhóm thực nghiệm, cần báo chính xác phân phối. Giá transaction bình quân có thể đổi do cơ cấu giao dịch/khuyến mãi, không tự đồng nghĩa cửa hàng thay giá niêm yết.

## 2. Quy tắc audit

- Đọc tám bảng cốt lõi; khử trùng toàn dòng, phát hiện/xử lý cách ly khóa xung đột nếu có; kiểm tra sáu quan hệ tham chiếu chính.
- Chuẩn hóa complete/completed và canceled/cancelled; chỉ lấy completed, Quantity và ActualSellingPrice dương, hữu hạn.
- Cửa sổ đầy đủ thứ Hai–Chủ nhật: 03/07/2023 đến hết tuần bắt đầu 22/12/2025, tổng 130 tuần. Không dùng hai tuần biên thiếu ngày.
- Giá tuần = tổng Quantity × ActualSellingPrice / tổng Quantity. Assert khóa SKU–tuần duy nhất, tổng lượng và tổng giá trị được bảo toàn.
- Tạo origin sau khi SKU đã có giá lịch sử; không cắt theo lần bán cuối trong tương lai. Nhãn tuần tới chỉ dùng khi có giao dịch, không forward-fill target. Baseline dùng giá quan sát gần nhất trước hoặc tại origin.
- Chia khoảng 70/15/15 theo tuần đích. Chỉ tính động học giá và sai số baseline trên train/validation. Số nhãn test chỉ được kiểm kê, không chấm điểm test trong audit này.

## 3. Kết quả

| Nội dung | Kết quả |
| --- | --- |
| Tệp raw | 27 CSV |
| Trùng toàn dòng SalesOrders / Products | 845 / 1; có thể loại với log |
| Khóa xung đột còn lại ở tám bảng kiểm tra | 0 sau loại bản trùng toàn dòng |
| Orphan ở sáu quan hệ kiểm tra | 0 |
| Dòng giao dịch sau lọc và lấy tuần đầy đủ | 553.261 |
| SKU có giá quan sát | 871 |
| Quan sát SKU–tuần có giao dịch | 68.317 |
| Số tuần quan sát mỗi SKU, P10 / P25 / median / P75 | 16 / 41,5 / 81 / 126 |
| SKU có ít nhất 32 tuần quan sát | 699 / 871 |
| Median độ phủ trong khoảng tuần bán đầu–cuối | 100%; P10 khoảng 67,97%; chỉ mô tả hồi cứu, không dùng làm cohort dự báo |
| Lượng bán/tuần có giao dịch, P10 / median / P90 | 2 / 7 / 19 đơn vị |
| Dòng giá thực bằng giá thường, sai số tuyệt đối ≤0,01 | 90,60% |
| Giảm giá nhưng PromotionID trống / giá thực vượt giá thường | 0 trong tập đã lọc |

Các cấu trúc khá sạch hoặc đều đặn không chứng minh nguồn là dữ liệu thật hay mô phỏng. Không có ingestion timestamp để xác thực độ trễ; danh mục là snapshot, chưa có lịch sử phiên bản.

| Tập | Khoảng tuần đích | Origin đủ điều kiện | Có nhãn | Độ phủ nhãn |
| --- | --- | --- | --- | --- |
| Train | 10/07/2023–24/03/2025 | 52.429 | 44.182 | 84,27% |
| Validation | 31/03/2025–04/08/2025 | 14.609 | 10.940 | 74,89% |
| Test | 11/08/2025–22/12/2025 | 16.730 | 12.324 | 73,66% |

Độ phủ trên cohort chỉ yêu cầu đã từng có giá là cách tiếp cận bảo thủ: có thể chứa SKU ngừng bán chưa được xác minh. Không diễn giải mọi tuần không có nhãn là lỗi hoặc hàng vẫn còn kinh doanh.

| Động học và baseline | Train | Validation |
| --- | --- | --- |
| Last-price WAPE | 0,975% | 1,086% |
| MAE theo tiền tệ nguồn chưa xác minh | 138,68 | 162,48 |
| Giá không đổi trong sai số 0,01 | 62,78% | 57,05% |
| Giá đổi >1% so với giá gần nhất | 28,10% (12.416 mẫu) | 30,22% (3.306 mẫu) |
| Giá đổi >5% | 6,39% (2.823 mẫu) | 7,12% (779 mẫu) |
| Giá đổi >10% | 1,32% (585 mẫu) | 1,53% (167 mẫu) |

Các ngưỡng là mô tả thăm dò, chưa phải scenario cuối đã khóa. Nhóm đổi giá là phân tích hậu nghiệm khi có nhãn, không phải thông tin có sẵn lúc dự báo. WAPE thấp nhưng có hàng nghìn mẫu đổi >1%; không kết luận bài quá dễ hoặc không có tín hiệu chỉ từ một độ đo aggregate.

## 4. Việc làm tiếp theo theo thứ tự

1. **Xác minh dataset card:** dữ liệu thật/mô phỏng, cách tạo/thu thập, license, tiền tệ, định nghĩa ActualSellingPrice và RegularUnitPrice. Nếu không xác minh được, ghi giới hạn và tránh tuyên bố hiệu quả thực tế doanh nghiệp.
2. **Khóa hợp đồng dữ liệu giá:** dùng pipeline mới có target_week/observation mask, không tái sử dụng nguyên mt_train/y_qty/risk cũ. Thêm audit ngoại lai theo SKU, thời điểm SKU ActiveFrom, quan hệ PromotionID và ngày chương trình; không loại dữ liệu chỉ vì model khó dự báo.
3. **Pilot nhỏ trên train/validation trước:** last-price, rolling-price, Ridge, LightGBM giá trực tiếp và LightGBM log-ratio; cùng origins/feature availability. Đánh giá WAPE, macro-SKU và nhóm biến động; chưa chọn theo test. Đây là gói việc tiếp theo, chưa chạy trong audit.
4. **Go/no-go cho model lớn:** nếu có cải thiện hoặc câu hỏi khoa học rõ dù model không thắng, tiếp tục 10 phương pháp với protocol đã thiết kế. Nếu chỉ copy persistence, gains không ổn định hoặc giá biến động không có thông tin đầu vào giải thích được, điều tra cơ chế giá/khuyến mãi trước khi tăng model.
5. **Dữ liệu thứ hai nếu cần:** ưu tiên lịch sử giá theo sản phẩm có timestamp, nhiều thay đổi và nguồn rõ; phân biệt giá niêm yết scrape với giá giao dịch. Không nối tùy tiện giá sản phẩm khác/tiền tệ khác. Dùng benchmark ngoài riêng để đánh giá khả năng khái quát; chưa có nguồn thứ hai được chọn/xác minh trong audit này.

Không có cải thiện trên pilot không tự chứng minh dữ liệu vô dụng: có thể cần feature khác hoặc đây là kết quả negative hữu ích. Nhưng khi mục tiêu là đóng góp phương pháp và khái quát, chỉ một bộ dữ liệu nguồn gốc chưa rõ sẽ hạn chế mức tuyên bố. Không đổi sang cold-start chỉ để tạo gap trong khi dữ liệu chủ yếu đã có lịch sử.