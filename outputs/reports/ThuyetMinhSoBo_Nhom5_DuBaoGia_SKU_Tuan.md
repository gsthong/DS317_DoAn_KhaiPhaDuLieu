# THUYẾT MINH SƠ BỘ ĐỀ TÀI

## DỰ BÁO GIÁ BÁN THỰC TẾ THEO SKU–TUẦN TRONG BÁN LẺ ĐIỆN MÁY

**Học phần:** DS317.R11 – Khai phá dữ liệu trong doanh nghiệp

**Nhóm thực hiện:** Nhóm 5

**Phiên bản:** Bổ sung định nghĩa toán học, nghiệp vụ, gap và phương pháp sau khảo sát 2023–2026 – 06/11/2026

**Trạng thái:** Bản đề xuất sơ bộ. Các mô hình, cấu hình và thực nghiệm bên dưới là kế hoạch, không phải kết quả đã đạt. Số liệu khảo sát thô được tách riêng tại Mục 5; không sử dụng số điểm mô hình chưa truy nguyên được trong tài liệu cũ.

## Phần A. Thông tin hành chính

| Nội dung | Thông tin |
| --- | --- |
| Tên tiếng Việt | Dự báo giá bán thực tế theo SKU–tuần trong bán lẻ điện máy |
| Tên tiếng Anh | Weekly SKU-Level Actual Selling Price Forecasting in Electronics Retail |
| Lớp – Nhóm | DS317.R11 – Nhóm 5 |
| Thành viên | Võ Đình Kiên (24520893, nhóm trưởng); Quách Tuấn Kiệt (24520911); Huỳnh Chí Kiên (24520880); Nguyễn Hữu Bảo Lộc (24520983); Đỗ Văn Lộc (24520977); Lê Sỹ Liêm (24520951); Trần Hồng Lĩnh (24520970) |
| Giảng viên hướng dẫn | TS. Nguyễn Gia Tuấn Anh – giữ theo hồ sơ Nhóm 5 hiện có, cần đối chiếu trước khi nộp |
| Thời gian | Học kỳ 1, năm học 2026–2027; lộ trình dự kiến 6 tuần kể từ khi chốt đề cương, điều chỉnh theo lịch học phần |

## Phần B. Nội dung chuyên môn

## Mục 1. Bối cảnh và lý do chọn đề tài

Trong bán lẻ điện máy, giá giao dịch thực tế của một SKU có thể khác giá niêm yết do khuyến mãi, chiết khấu và cơ cấu giao dịch theo kênh. Việc chỉ theo dõi giá danh mục chưa phản ánh đầy đủ mức giá bình quân doanh nghiệp thực thu. Một dự báo ngắn hạn về giá bán thực tế có thể hỗ trợ chuyên viên ngành hàng rà soát biến động và chuẩn bị thông tin cho kế hoạch kinh doanh.

Nhóm lựa chọn một khâu nghiệp vụ cụ thể: tại cuối mỗi tuần, ước lượng giá giao dịch bình quân của từng SKU trong tuần kế tiếp từ dữ liệu đã quan sát. Đầu ra là thông tin tham khảo để chuyên viên rà soát, không tự động thay đổi giá bán. Mức hữu ích được kiểm chứng trước hết bằng sai số dự báo so với phương pháp đơn giản là giữ nguyên giá gần nhất.

Đề tài chỉ giải quyết một bài toán hồi quy có yếu tố thời gian. Kiểm soát chất lượng dữ liệu là bước bảo đảm đầu vào và độ tin cậy của đánh giá, không phải một nhiệm vụ dự đoán thứ hai. Nhóm không triển khai Transformer đa nhiệm, phân loại rủi ro tồn kho, dự báo lượng bán hoặc tối ưu hóa lợi nhuận trong phạm vi bản đề xuất này.

### 1.1. Quy trình nghiệp vụ được ứng dụng

Đề tài được đặt tại bước **rà soát giá thực thu và chuẩn bị kế hoạch tuần kế tiếp của chuyên viên ngành hàng**. Đây là quy trình ứng dụng đề xuất cho doanh nghiệp bán lẻ giả định, không phải quy trình đã khảo sát và xác nhận tại một doanh nghiệp thật. Một kỳ xử lý bắt đầu sau khi tuần t đóng sổ và kết thúc khi kết quả thực tế tuần t+1 được đối chiếu.

| Bước nghiệp vụ | Vai trò và hành động | Đầu ra / điểm kiểm soát |
| --- | --- | --- |
| 1. Chốt giao dịch tuần t | Nhân sự dữ liệu tiếp nhận đơn hàng, dòng hàng và danh mục tại cutoff | Snapshot dữ liệu, thời điểm chốt và phiên bản; chỉ nhận sự kiện ≤ t, ghi rõ giả định về độ trễ cập nhật |
| 2. Kiểm tra và phê duyệt dữ liệu | Nhân sự dữ liệu kiểm tra khóa, liên kết, trạng thái, lượng/giá và tổng sau join | Lỗi cứng: dừng/cách ly; thiếu quan sát do không bán: giữ cờ thiếu, không gán nhãn giả |
| 3. Lập dự báo tuần t+1 | Pipeline tổng hợp SKU–tuần, tạo đặc trưng và chạy mô hình đã khóa | Giá dự báo, giá gần nhất, độ mới lịch sử và trạng thái đủ/không đủ điều kiện |
| 4. Rà soát ngành hàng | Chuyên viên so giá dự báo với giá gần nhất; sắp xếp SKU có thay đổi dự kiến lớn để kiểm tra | Danh sách rà soát và nhận xét; không coi chênh lệch là xác suất rủi ro hay mức giá nên niêm yết |
| 5. Sử dụng thông tin kế hoạch | Quản lý ngành hàng tham khảo kết quả cùng chính sách giá/khuyến mãi nội bộ | Quyết định vẫn do con người phê duyệt; đề tài không tự tối ưu hay cập nhật giá POS |
| 6. Đối chiếu tuần t+1 | Khi có giao dịch thực tế, nhân sự phân tích đối chiếu dự báo và giá quan sát | Sai số, độ phủ nhãn, lỗi theo nhóm SKU/tuần; không chấm tuần không bán như có giá thực |

Luồng tóm tắt: **đóng sổ → kiểm tra dữ liệu → dự báo → chuyên viên rà soát → tham khảo lập kế hoạch → đối chiếu thực tế**. Giá trị nghiệp vụ dự kiến là cung cấp thêm thông tin ngắn hạn và hỗ trợ ưu tiên rà soát. Chưa khẳng định tiết kiệm thời gian hay tăng lợi nhuận khi chưa đo thực tế.

## Mục 2. Mục tiêu đề tài

### 2.1. Mục tiêu tổng quát

Xây dựng và đánh giá quy trình dự báo giá bán thực tế tuần kế tiếp ở mức SKU–tuần, từ dữ liệu giao dịch đã được kiểm tra chất lượng, bảo đảm đặc trưng chỉ sử dụng thông tin có sẵn tại thời điểm dự báo.

### 2.2. Mục tiêu cụ thể và tiêu chí hoàn thành

| Mục tiêu | Tiêu chí hoàn thành |
| --- | --- |
| Xác định đúng dữ liệu và biến mục tiêu | Có từ điển dữ liệu, quy tắc chọn giao dịch, công thức giá, chính sách tuần không bán và sơ đồ quan hệ |
| Kiểm soát dữ liệu theo quy trình | Có báo cáo kiểm tra trước/sau, nhật ký loại/cách ly/gộp dòng và kiểm tra bảo toàn tổng lượng, tổng giá trị |
| Xây dựng bảng modeling đúng thời điểm | Khóa (sku_id, origin_week) duy nhất; có target_week; không dùng tương lai làm đặc trưng; bảng train/validation/test tái lập được |
| Đối sánh có căn cứ | Chạy baseline giá gần nhất, giá trung bình trượt, Ridge và LightGBM trên cùng tập đánh giá và cùng thông tin đầu vào |
| Phân tích tính hữu ích | Báo cáo sai số tổng thể, theo SKU/ngành hàng và trên tuần giá biến động; xác định điều kiện mô hình tốt hoặc kém hơn baseline |
| Bàn giao tái lập | Notebook chạy lại được, cấu hình/chia tập/log và bảng kết quả xuất tự động; bản trình bày đầu ra minh họa |

Không đặt trước ngưỡng R² hoặc WAPE tùy ý để bảo đảm một mô hình đạt yêu cầu. Mô hình phức tạp chỉ được khuyến nghị khi có cải thiện có thể kiểm chứng so với baseline mạnh; nếu không, nhóm báo cáo trung thực và ưu tiên phương pháp đơn giản.

### 2.3. Mục tiêu phương pháp đề xuất

Nhóm đề xuất kiểm chứng **hồi quy phần thay đổi giá quanh giá quan sát gần nhất, có đặc trưng mức độ quan sát của lịch sử**. Mục tiêu không phải tạo thêm đầu phân loại rủi ro, mà cải thiện cùng một dự báo giá qua ba thành phần: (1) chuẩn hóa khác biệt mặt bằng giá giữa SKU bằng log-ratio; (2) biểu diễn tuần không quan sát và độ mới của giá bằng mask/recency; (3) tùy chọn phối hợp với baseline giá gần nhất để hạn chế dự báo dao động khi bằng chứng lịch sử yếu.

| Mục tiêu kỹ thuật | So sánh để kiểm chứng | Tiêu chí diễn giải |
| --- | --- | --- |
| Học biến động thay vì chỉ học mức giá giữa SKU | Cùng learner và features: giá trực tiếp, log-price, log-ratio | So WAPE/MAE và macro-WAPE trên cùng tập; không dựa riêng R² |
| Khai thác đúng mức độ quan sát | Bỏ/thêm mask, recency và tỷ lệ tuần có giá | Báo riêng nhóm lịch sử thưa/dày, ngưỡng xác định từ train |
| Đo giá trị thông tin ngoại sinh | Target-only so với thêm qty/discount quá khứ và lịch biết trước | Chỉ giữ lợi ích còn tồn tại sau kiểm tra cutoff và ablation |
| Hạn chế dao động không cần thiết | Mô hình residual có/không blending; đối sánh last-price | Kiểm tra cả toàn bộ test và nhóm tuần giá biến động hậu nghiệm |
| Xác định tính cạnh tranh và chi phí | Baseline truyền thống, supervised mới và foundation models 2023–2026 | Báo cải thiện, độ ổn định, thời gian/RAM và failures; chưa cam kết vượt SOTA |

Đây là mục tiêu và giả thuyết thực nghiệm; log-ratio, mask hay blending là kỹ thuật đã biết, không được trình bày như thuật toán mới chưa từng có. Lịch sử ngắn/thưa là điều kiện sẽ đo bằng EDA, không tự đồng nghĩa cold-start hoặc few-shot learning. SKU chưa có giá lịch sử nằm ngoài phương pháp anchor ở bản này.

## Mục 3. Phát biểu bài toán khai phá dữ liệu

### 3.1. Đơn vị phân tích và thời điểm dự báo

- Một mẫu là một SKU i tại cuối tuần t, gọi là origin_week. Tuần quy ước từ thứ Hai đến Chủ nhật; target_week là tuần t+1.
- Đầu vào gồm lịch sử giao dịch đến hết tuần t, đặc trưng danh mục được xác định là sẵn có tại thời điểm đó và các biến lịch của tuần t+1.
- Đầu ra duy nhất là giá bán thực tế bình quân gia quyền của SKU i trong tuần t+1.
- Đối tượng dự báo chính là SKU có ít nhất một giao dịch hợp lệ trong quá khứ. SKU chưa có lịch sử giá nằm ngoài phạm vi đánh giá chính và được ghi rõ trong báo cáo độ phủ.

### 3.2. Định nghĩa nhãn

Với các dòng giao dịch hợp lệ j của SKU i trong tuần t+1:

**y(i,t+1) = Σ[Quantity(j) × ActualSellingPrice(j)] / Σ[Quantity(j)].**

Đây là giá bình quân một đơn vị sản phẩm, không phải doanh thu, tổng giá trị đơn hàng hoặc giá tối ưu. Đơn vị tiền tệ được giữ theo dữ liệu nguồn; chưa quy đổi hay gán ký hiệu tiền khi chưa xác minh được metadata.

Nếu tuần đích không có giao dịch hợp lệ thì giá giao dịch không quan sát được. Nhóm không gán nhãn bằng 0 và không forward-fill nhãn để biến giá giả lập thành sự thật. Khi triển khai minh họa vẫn có thể tạo dự báo cho SKU đủ điều kiện; khi đánh giá chỉ chấm điểm các tuần có nhãn quan sát, đồng thời công bố tỷ lệ nhãn quan sát được trên toàn bộ các cặp SKU–tuần đủ điều kiện dự báo. Kết luận do đó giới hạn ở giá có điều kiện trên tuần phát sinh giao dịch.

### 3.3. Phạm vi thông tin và đầu ra nghiệp vụ

Giá, lượng bán và chiết khấu quan sát trong tuần t+1 chỉ được dùng tạo nhãn hoặc phân tích lỗi, không làm đầu vào. Lịch khuyến mãi tương lai không dùng trong mô hình chính vì bộ CSV không chứng minh thời điểm lịch được công bố. Tồn kho chưa đưa vào mô hình chính để tránh mở rộng sang tái lập và đánh giá rủi ro tồn kho.

Chuyên viên ngành hàng nhận bảng gồm SKU, tuần dự báo, giá gần nhất, giá dự báo và mức thay đổi dự kiến. Họ đối chiếu thông tin với kế hoạch nội bộ trước khi quyết định. Bảng này không được diễn giải là khuyến nghị định giá tự động hoặc xác suất rủi ro.

### 3.4. Định nghĩa ký hiệu, tham số và hàm toán học

| Ký hiệu | Định nghĩa / miền giá trị |
| --- | --- |
| i ∈ {1,…,N}; t | SKU thứ i và chỉ số tuần lịch; N là số SKU đủ điều kiện theo quá khứ |
| h = 1; L | Chân trời một tuần; L là số tuần lịch trong cửa sổ đầu vào, chọn trong {8,16,32} trên validation |
| J(i,s); q_j; p_j | Tập dòng giao dịch hợp lệ của SKU i trong tuần s; số lượng q_j > 0 và giá đơn vị p_j = ActualSellingPrice_j > 0 |
| Q(i,s); V(i,s) | Tổng lượng Q(i,s) = Σ q_j; tổng giá trị V(i,s) = Σ q_j × p_j, lấy tổng trên J(i,s) |
| m(i,s); P(i,s) | m(i,s) = 1 nếu Q(i,s) > 0, ngược lại 0; P(i,s) = V(i,s)/Q(i,s) chỉ xác định khi m(i,s)=1 |
| τ(i,t); a(i,t) | τ(i,t) = max{s ≤ t: m(i,s)=1}; a(i,t)=P(i,τ(i,t)) là giá neo gần nhất; chỉ dự báo khi τ tồn tại |
| d(i,t); c(i,t) | Độ mới d(i,t)=t−τ(i,t), tính theo tuần; độ phủ c(i,t)=Σ m(i,s)/L trên s=t−L+1,…,t; tuần trước lần quan sát đầu có mask 0 |
| z_i; u(i,s); k(t+1) | Danh mục SKU giả định sẵn có/ổn định; ngoại sinh quá khứ; biến lịch tuần đích biết trước tại t |
| x(i,t) ∈ R^D | Vector D đặc trưng sau mã hóa từ cửa sổ giá/quan sát, u(i,s), z_i, d, c và k(t+1); D phụ thuộc tập feature và encoder fit trên train |
| θ; η; λ | Tham số học của mô hình; siêu tham số cấu hình η; hệ số blending λ ∈ [0,1], chọn trên validation |

Với s từ t−L+1 đến t, đầu vào lịch sử giữ cặp (P(i,s), m(i,s)); giá không quan sát là missing chứ không bằng 0. Nếu implementation cần điền, chỉ dùng giá đã quan sát trước s, giữ mask; trước quan sát đầu dùng missing/padding có mask theo adapter, không backfill từ tương lai. Ngoại sinh u chỉ gồm thông tin sẵn có ở cutoff; k gồm lịch, không chứa giá/khuyến mãi thực hiện tương lai chưa được xác nhận.

**Hàm dự báo tổng quát:** y_hat(i,t+1)=f_θ(x(i,t)) > 0. Nhãn y(i,t+1)=P(i,t+1) chỉ tồn tại khi m(i,t+1)=1. Bộ dữ liệu học D_train gồm các cặp (x(i,t),y(i,t+1)) có nhãn quan sát và tuần đích thuộc khoảng train. Không dùng giá điền làm nhãn và không bỏ qua tuần lịch để lấy lần bán kế tiếp làm t+1.

**Hàm mục tiêu đánh giá chính:** WAPE = 100 × Σ abs(y−y_hat) / Σ y trên cùng tập nhãn quan sát dương. Đây là tỷ lệ sai số dự báo giá, không phải tổn thất doanh thu. MAE, RMSE, macro-WAPE và độ phủ nhãn được báo bổ sung.

Tập dự báo tại t là E_t={i: τ(i,t) tồn tại và dữ liệu đầu vào qua kiểm tra cứng}. Đầu ra O_t gồm (i, t+1, a(i,t), y_hat(i,t+1), Δ_hat(i,t), d(i,t), c(i,t)), trong đó Δ_hat=100×(y_hat/a−1). Sau tuần đích mới biết nhãn quan sát để chấm điểm. Tỷ lệ có nhãn = Σ_t Σ_{i∈E_t} m(i,t+1) / Σ_t số phần tử E_t; không được dùng m(i,t+1) để quyết định trước SKU nào mới được nhận dự báo.

Giới hạn thống kê: quá trình học/đánh giá phản ánh giá trên các tuần có giao dịch. Không suy ra giá giao dịch không quan sát khi không bán, quan hệ nhân quả của khuyến mãi, hay giá tối ưu. Cutoff sự kiện được kiểm tra từ CSV; tính sẵn có thực tế còn phụ thuộc giả định độ trễ ghi nhận do chưa có ingestion timestamp.

## Mục 4. Tổng quan công trình liên quan và định hướng kế thừa

### 4.1. Các hướng phương pháp tham khảo

| Nguồn/hướng | Nội dung kế thừa | Giới hạn khi áp dụng |
| --- | --- | --- |
| Hyndman và Athanasopoulos, Forecasting: Principles and Practice, bản 3 [2] | Dự báo ngây thơ, phương pháp đơn giản và đánh giá theo thứ tự thời gian | Là cơ sở phương pháp, không phải bằng chứng đã giải quyết đúng dữ liệu giá điện máy của nhóm |
| Ke và cộng sự, LightGBM, NeurIPS 2017 [3] | Gradient boosting trên đặc trưng bảng, mô hình phi tuyến đối sánh với Ridge | Bài thuật toán tổng quát; không lấy kết quả trên dữ liệu khác làm mốc điểm trực tiếp |
| Các nghiên cứu dự báo giá bán lẻ trực tiếp | Cần khảo sát bổ sung bài có giá giao dịch làm mục tiêu, có horizon và quy tắc đánh giá rõ ràng | Chưa đủ bằng chứng trong hồ sơ hiện tại để tuyên bố khoảng trống SOTA hoặc mức vượt trội |

### 4.2. Cách khảo sát và câu hỏi nghiên cứu

Nhóm sẽ chọn ít nhất ba nghiên cứu ứng dụng phù hợp để hoàn thiện bản chính thức. Mỗi bài được ghi nhận: nguồn và vị trí bằng chứng; đối tượng/ngành hàng; dữ liệu; nhãn giá; thời điểm dự báo; horizon; cách chia tập; baseline; độ đo; hạn chế. Không đồng nhất nghiên cứu dự báo nhu cầu hoặc tối ưu giá với nghiên cứu dự báo giá giao dịch. Bài về nhu cầu chỉ dùng tham khảo kỹ thuật nếu phù hợp.

Câu hỏi thực nghiệm của nhóm là: (1) lịch sử giá và các đặc trưng giao dịch đến tuần t có giúp dự báo tốt hơn giữ nguyên giá gần nhất không; (2) cải thiện có duy trì qua các giai đoạn thời gian và ngành hàng không; (3) lượng bán, chiết khấu quá khứ và đặc trưng lịch đóng góp như thế nào?

Đóng góp dự kiến là một quy trình đối sánh có kiểm soát dữ liệu và phân tích giới hạn trên bối cảnh dữ liệu đã chọn. Nhóm không tuyên bố phát minh thuật toán, giải quyết khoảng trống toàn ngành hoặc vượt SOTA khi chưa có bằng chứng.

### 4.3. Kết quả khảo sát phương pháp 2023–2026 và khoảng trống kỹ thuật

Hồ sơ related work đi kèm đã đối chiếu 10 phương pháp: TiDE, TSMixer, iTransformer, TimeMixer, TimeXer, Chronos-2, Moirai 2.0, TabPFN-TS, TimesFM-3 và TiRex-2 [4]. Đây chủ yếu là phương pháp forecasting tổng quát có thể áp dụng, không phải 10 nghiên cứu trực tiếp giá giao dịch điện máy. TSMixer M5/Chronos-2 Rossmann liên quan retail demand; TimeXer EPF liên quan giá điện. Không so điểm công bố trên các dữ liệu đó như cùng bài toán giá SKU của nhóm.

Các mô hình mới đã hỗ trợ nhiều khả năng: TimeXer tách target/ngoại sinh; Chronos-2, TimesFM-3, TiRex-2 có covariates và quantiles. Moirai2 có missing-aware embedding nhưng bản v2 bỏ covariates/cross-variate. Vì vậy không chọn “thiếu ngoại sinh”, “thiếu dự báo xác suất” hay “không xử lý missing” làm gap chung. Phần còn cần giải quyết trong bối cảnh nhóm là **thiết kế và kiểm chứng học biến động giá quanh một baseline persistence mạnh, dưới quy tắc nhãn quan sát và thông tin sẵn có thực tế**.

| Khoảng trống kỹ thuật ứng viên | Căn cứ và giới hạn | Cách nhóm giải quyết / bằng chứng cần có |
| --- | --- | --- |
| Biểu diễn mục tiêu phù hợp giá SKU khác mặt bằng và có persistence | Các kiến trúc tiên tiến không tự bảo đảm hơn last-price trên panel giá này; chưa chứng minh mọi SKU đều ít biến động | So raw/log/log-ratio với cùng learner; kiểm tra tuần ổn định/biến động và macro-SKU |
| Phân biệt missing input với nhãn không quan sát do không bán | Missing-aware embedding không tự xác định đúng target policy hoặc khắc phục thiên lệch chọn tuần có giao dịch | Giữ observation mask, thêm recency/coverage; không impute truth; báo coverage và giới hạn conditional evaluation |
| Ngoại sinh hợp lệ tại cutoff | Model nhận được covariates không chứng minh dữ liệu tương lai thật sự biết trước; CSV chưa có lịch sử công bố khuyến mãi | Feature availability ledger; loại biến tương lai chưa chứng minh; ablation history-only/valid covariates |
| Thiếu đối sánh đồng nhất cho đúng cohort và horizon của nhóm | Trong các nguồn đã khảo sát chưa xác minh benchmark đúng actual SKU-week price này | Cùng origin/target-week, track target-only và valid-covariates; lưu prediction keys, version, failures và chi phí |

Đây là gap kỹ thuật/đánh giá **trong phạm vi ứng dụng và các nguồn đã đọc**, chưa là bằng chứng rằng chưa ai từng dùng residual, mask hoặc persistence. Chỉ khẳng định cải thiện sau thực nghiệm; khảo sát nghiên cứu domain trực tiếp vẫn cần bổ sung.

### 4.4. Khoảng trống ứng dụng và đóng góp dự kiến

Khoảng trống ứng dụng là thiếu một quy trình minh họa thống nhất từ giao dịch hợp lệ đến dự báo và rà soát giá thực thu tuần kế tiếp, phù hợp dữ liệu công khai hiện có. Nguồn generic forecasting hoặc retail demand chưa tự cung cấp định nghĩa giá giao dịch SKU, chính sách tuần không bán và quy trình sử dụng tại chuyên viên ngành hàng của đề tài này. Đây không phải tuyên bố doanh nghiệp ngoài thực tế đều thiếu hệ thống như vậy.

Đóng góp ứng dụng dự kiến gồm: (1) hợp đồng dữ liệu và kiểm tra bảo toàn sau join/tổng hợp; (2) giá dự báo gắn giá tham chiếu, độ mới và độ phủ lịch sử; (3) đối chiếu thực tế theo tuần có nhãn, công bố trường hợp không đủ dữ liệu; (4) hồ sơ tái lập code–data–model–metrics. Dashboard nếu có chỉ là kênh trình bày, không là bằng chứng novelty. Chưa tuyên bố tối ưu lợi nhuận, giảm rủi ro tồn kho hoặc tiết kiệm chi phí khi thiếu đánh giá nghiệp vụ tương ứng.

## Mục 5. Mô tả dữ liệu và khảo sát sơ bộ

### 5.1. Nguồn và phạm vi sử dụng

Dữ liệu Electronics Sales Dataset (B.Tech style) do tài khoản fahdelatiby công bố trên Kaggle [1], đang lưu trong thư mục data/raw của dự án. Đây là bộ dữ liệu công khai mang cấu trúc nghiệp vụ bán lẻ; không coi là log vận hành đã được doanh nghiệp xác nhận. Nguồn gốc tạo dữ liệu, đơn vị tiền và điều kiện giấy phép cần đối chiếu với mô tả tác giả trước khi nộp/chia sẻ lại dữ liệu.

Đã kiểm kê được 27 tệp CSV trong bản dữ liệu cục bộ. Quy trình chính chỉ sử dụng các bảng cần thiết sau, không tích hợp toàn bộ 27 bảng chỉ để tăng quy mô:

| Bảng | Quy mô thô kiểm tra ngày 06/11/2026 | Vai trò và trường chính |
| --- | --- | --- |
| SalesOrders | 322.577 dòng × 8 cột | SalesOrderID, OrderDate, OrderStatus; xác định thời gian và trạng thái |
| SalesOrderLines | 579.572 dòng × 9 cột | SalesOrderLineID, SalesOrderID, LineNumber, SKU_ID, Quantity, RegularUnitPrice, ActualSellingPrice, PromotionID |
| ProductVariants | 902 dòng × 8 cột | SKU_ID → ProductID; liên kết SKU và thông số sản phẩm |
| Products | 576 dòng × 9 cột | ProductID, BrandID, SubcategoryID, ActiveFrom, ActiveTo |
| Brands | 66 dòng × 2 cột | BrandID, BrandName |
| Subcategories | 65 dòng × 3 cột | SubcategoryID → CategoryID |
| Categories | 8 dòng × 2 cột | CategoryID, CategoryName |
| Promotions | 34 dòng × 5 cột | Chỉ hỗ trợ kiểm tra tham chiếu và khoảng ngày; không mặc nhiên dùng lịch tương lai |

Số dòng trên là số thô trước chuẩn hóa và khử trùng; số SKU và số mẫu modeling cuối cùng phải xuất lại từ pipeline. Cửa sổ nghiên cứu dự kiến 01/07/2023–31/12/2025; bỏ tuần biên không đủ bảy ngày sau khi chốt lịch tuần.

### 5.2. Một số quan sát đã kiểm tra trực tiếp

- Sau trim và lowercase, trạng thái đơn gồm completed: 309.087; complete: 505; cancelled: 12.969; canceled: 16. Cần ánh xạ complete → completed và canceled → cancelled bằng bảng quy tắc có lưu vết.
- Trong SalesOrderLines thô: chưa phát hiện dòng trùng hoàn toàn hoặc trùng cặp (SalesOrderID, LineNumber); Quantity và ActualSellingPrice không thiếu, không có giá trị ≤ 0. Kết quả này không thay thế kiểm tra khóa SalesOrderLineID, quan hệ tham chiếu và chất lượng giá.
- Chưa công bố số mẫu sau làm sạch, kết quả mô hình hay phần trăm cải thiện trong bản này. Các bảng interim/split cũ thuộc bài toán lượng bán–rủi ro không được xem là bộ modeling giá đã hoàn tất.

## Mục 6. Quy trình kiểm tra và tiền xử lý dữ liệu

### 6.1. Luồng xử lý và điểm kiểm soát

**CSV gốc bất biến → kiểm kê và kiểm tra schema → chuẩn hóa/làm sạch và cách ly → nối giao dịch với danh mục → tổng hợp SKU–tuần → tạo đặc trưng/nhãn → chia tập thời gian → fit biến đổi trên train → kiểm tra cuối → mô hình và đánh giá.**

| Bước | Kiểm tra và xử lý | Bằng chứng cần lưu |
| --- | --- | --- |
| 1. Kiểm kê | Tên file, checksum, số dòng/cột, kiểu dữ liệu, khóa dự kiến, thời gian min/max, tỷ lệ thiếu | Data inventory và metadata lần chạy |
| 2. Khóa và schema | Tách trùng toàn dòng với trùng khóa; kiểm tra khóa đơn, khóa dòng, khóa SKU/danh mục; parse ngày và số | Bảng thống kê lỗi, ví dụ dòng lỗi, quyết định xử lý |
| 3. Chuẩn hóa | Trim/case trạng thái; ánh xạ bằng quy tắc rõ ràng; lọc đơn completed; kiểm tra Quantity > 0 và ActualSellingPrice > 0 | Số dòng trước/sau mỗi quy tắc, lý do loại hoặc cách ly |
| 4. Kiểm tra liên kết | Dòng đơn → đơn; SKU → variant → product → brand/subcategory → category; kiểm tra phía danh mục duy nhất trước nối many-to-one | Tỷ lệ orphan; số dòng, lượng và giá trị trước/sau join |
| 5. Tổng hợp | Tạo lịch tuần chuẩn; tính tổng Quantity, tổng Quantity × ActualSellingPrice và giá bình quân gia quyền | Khóa SKU–tuần duy nhất; đối chiếu tổng lượng và giá trị với bảng giao dịch |
| 6. Đặc trưng/nhãn | Tạo lưới tuần lịch theo SKU; giữ giá quan sát và dấu thiếu riêng; lấy nhãn đúng tuần t+1, không phải lần giao dịch kế tiếp | target_week − origin_week = 7 ngày; cờ có nhãn; độ phủ |
| 7. Chia tập/biến đổi | Chia theo target_week; fit bộ điền thiếu, chuẩn hóa và mã hóa chỉ trên train | Ngày chia, danh sách cột, thông số fit, số mẫu từng tập |
| 8. Kiểm tra bàn giao | Khóa không trùng; nhãn có giá trị hữu hạn dương; không có cột tương lai trong X; mọi phép biến đổi truy nguyên được | Checklist đạt/chưa đạt; cấu hình và báo cáo kiểm tra cuối |

Nếu trùng hoàn toàn thì giữ một bản và ghi log. Nếu cùng khóa nhưng khác nội dung thì cách ly để kiểm tra, không tự chọn bản đầu/cuối khi không có timestamp cập nhật. Với khóa hoặc nhãn cốt lõi thiếu, không tự bịa dữ liệu để nối hay tạo nhãn. Dòng danh mục chưa khớp được ghi nhận; thiếu nhóm phụ trợ có thể gắn unknown nhưng không được làm tăng số dòng giao dịch.

### 6.2. Khung kiểm tra chất lượng dữ liệu

| Chiều chất lượng | Quy tắc áp dụng | Phản ứng và giới hạn |
| --- | --- | --- |
| Đầy đủ – Completeness | Đo thiếu khóa, ngày, Quantity, ActualSellingPrice; đo riêng thuộc tính danh mục và PromotionID | Khóa/nhãn thiếu: cách ly; PromotionID trống có thể là không khuyến mãi, không tự kết luận dữ liệu lỗi |
| Duy nhất – Uniqueness | Đo trùng toàn dòng, trùng khóa thực thể và trùng (sku_id, origin_week) | Không chấp nhận trùng khóa modeling; xử lý theo nguyên nhân và lưu số dòng tác động |
| Hợp lệ – Validity | Kiểu ngày/số, miền trạng thái, Quantity > 0, giá > 0, giá trị hữu hạn | Lỗi cứng cách ly; ngưỡng giá tuyệt đối không áp tùy ý cho mọi ngành hàng |
| Nhất quán – Consistency | Khóa ngoại; phép nối đúng cardinality; công thức giá; bảo toàn tổng lượng/giá trị | Join làm nhân dòng hoặc lệch tổng ngoài sai số số thực: dừng bước xử lý và sửa |
| Chính xác – Accuracy | Kiểm tra đối chiếu chéo giá và lượng giữa các biểu diễn, xem mẫu giá bất thường theo SKU/ngành hàng | Chỉ là bằng chứng hợp lý nội bộ; không đồng nghĩa xác minh đúng thực tế vì thiếu hóa đơn/hệ thống gốc |
| Kịp thời – Timeliness | Báo ngày giao dịch, khoảng thời gian và khả năng chứng minh thông tin sẵn có ở cutoff | Có thể kiểm tra timestamp sự kiện; độ trễ ghi nhận thực tế là N/A nếu thiếu ingestion timestamp, không chấm đạt 100% |

Với mỗi quy tắc, lưu số dòng được đánh giá, số vi phạm, tỷ lệ vi phạm và số dòng không áp dụng. Tỷ lệ đạt = 1 − số vi phạm / số được đánh giá, chỉ tính khi mẫu số > 0. Báo cáo trước/sau trên cùng định nghĩa, kèm số dòng bị loại để tránh tạo cảm giác chất lượng tăng chỉ vì xóa dữ liệu. Không gộp sáu chiều thành một điểm tổng tùy ý; công bố rõ độ phủ và N/A.

### 6.3. Xử lý tuần không bán, ngoại lai và thuộc tính thời gian

- Không có giao dịch trong tuần không đồng nghĩa lỗi thiếu giá; giữ chỉ báo price_observed = 0. Khi không biết ngày hàng ngừng kinh doanh, không tự suy rằng mọi khoảng trống là sản phẩm còn bán.
- Tạo các origin theo lịch tuần trong cửa sổ nghiên cứu sau khi SKU có lịch sử hợp lệ; không dùng ngày bán cuối cùng trong toàn bộ dữ liệu tương lai để quyết định SKU còn thuộc tập dự báo ở quá khứ. Dữ liệu ActiveTo thiếu hoặc không có lịch sử phiên bản không được dùng như ground truth vòng đời.
- Có thể forward-fill giá quá khứ để tạo last_observed_price, kèm số tuần kể từ lần bán gần nhất; tuyệt đối không backfill từ tương lai, không dùng giá điền làm nhãn.
- Giá cao hoặc chiết khấu bất thường là cảnh báo mềm để kiểm tra. Không tự loại giá vượt một trần chung, không cắt theo phân vị của toàn bộ dữ liệu. Nếu dùng ngưỡng thống kê cho đặc trưng, học ngưỡng từ train; giữ nguyên nhãn test hợp lệ.
- Các thuộc tính danh mục không có thời điểm cập nhật được mô tả là snapshot giả định ổn định. Chạy đối chứng bỏ nhóm snapshot để kiểm tra mức phụ thuộc; không tuyên bố point-in-time hoàn hảo.

### 6.4. Đặc trưng dự kiến

| Nhóm | Ví dụ | Điều kiện sử dụng |
| --- | --- | --- |
| Lịch sử giá | Giá quan sát tuần t; last_observed_price; giá trễ 1/2/4 tuần; trung bình/độ lệch chuẩn 4/8 tuần | Cửa sổ kết thúc ở t; chỉ dựa vào tuần ≤ t; phân biệt quan sát và điền |
| Giao dịch quá khứ | Lượng bán tuần t và trung bình 4 tuần; chiết khấu bình quân; tỷ lệ lượng có PromotionID | Chiết khấu tính từ giá thực tế và giá thường hợp lệ; RegularUnitPrice không dương thì không tính tỷ lệ |
| Lịch | Tháng, tuần trong năm, sin/cos mùa vụ của tuần đích | Tính được trước thời điểm dự báo, không lấy thông tin doanh số tương lai |
| Danh mục | SKU, thương hiệu, ngành hàng | Mã hóa fit trên train; mã mới có cơ chế unknown; kiểm tra tính duy nhất trước nối |
| Độ thưa | Số tuần từ lần bán gần nhất, số tuần có giá quan sát trong cửa sổ | Chỉ tích lũy từ quá khứ |

Mọi đặc trưng có nhật ký định nghĩa: công thức, nguồn, cửa sổ và thời điểm sẵn có. Không dùng y_qty, risk, cov_fwd, FutureSales hoặc giá trị thực của tuần đích làm X.

## Mục 7. Phương pháp khai phá dữ liệu dự kiến

### 7.1. Phương pháp đề xuất: hồi quy biến động giá có neo và thông tin quan sát

**Bước 1 – Đặt neo và biến đổi nhãn.** Với a(i,t)>0 được xác định hoàn toàn từ quá khứ, đặt r(i,t+1)=ln[y(i,t+1)/a(i,t)]. r=0 tương ứng giữ nguyên giá; r chỉ được tính cho mẫu có nhãn quan sát. Lựa chọn này nhằm giảm phụ thuộc vào mặt bằng giá tuyệt đối giữa SKU, không tự bảo đảm cải thiện.

**Bước 2 – Tạo đầu vào.** x(i,t) gồm giá/biến động quá khứ, mask quan sát, d(i,t), c(i,t), lượng và chiết khấu ≤t, danh mục theo giả định snapshot và lịch biết trước. Mọi thống kê mùa vụ/imputation/mã hóa học từ train hoặc lịch sử hợp lệ tại cutoff; target-week không tham gia tạo đặc trưng.

**Bước 3 – Học residual.** Chọn g_θ là LightGBM regressor trong phương án triển khai đầu tiên, với cùng bộ feature và ngân sách tuning khi đối sánh raw/log/log-ratio. Bài toán tối ưu trên M mẫu train quan sát là:

**θ_hat(η) = argmin_θ { (1/M) Σ_{(i,t)∈D_train} [r(i,t+1) − g_θ(x(i,t))]² + Ω_η(θ) }.**

Ω_η là thành phần regularization của learner, chẳng hạn phạt leaf weights của LightGBM; η điều khiển cấu hình cây/regularization. Loss này học trên log-ratio, không đồng nhất với tối ưu trực tiếp WAPE giá; vì vậy lựa chọn cấu hình phải dựa vào dự báo đã hoàn nguyên trên validation. Không suy exp(g_θ) là kỳ vọng giá không chệch khi chưa có hiệu chỉnh và giả định phân phối.

**Bước 4 – Hoàn nguyên và tùy chọn blending.** Giá residual y_hat_res(i,t+1)=a(i,t)×exp[g_θ(x(i,t))]. Đầu ra cuối cùng:

**y_hat(i,t+1;λ)=λ×a(i,t)+(1−λ)×y_hat_res(i,t+1), với λ∈{0;0,25;0,5;0,75;1}.**

λ=0 là residual model, λ=1 là last-price. Chọn η và λ toàn cục bằng WAPE validation theo quy tắc đã khóa; không dùng nhãn test hoặc nhóm price-change tương lai để chọn/gating. Nếu λ=1 tốt nhất, kết luận bằng chứng chưa ủng hộ phần residual trong cấu hình đó, không gọi là mô hình mới đã vượt baseline.

**Bước 5 – Kiểm chứng.** Ablation lần lượt raw price/log-price/log-ratio; bỏ/thêm mask–recency; bỏ/thêm ngoại sinh; λ=0 so với λ chọn validation. So với baseline và các model SOTA trên cùng tập quan sát. Các bước này cùng phục vụ một nhãn giá; không sinh nhãn rủi ro và không thêm đầu dự báo lượng bán.

### 7.2. Mô hình cơ sở và kế hoạch đối sánh mở rộng

| Phương pháp | Vai trò | Cấu hình sơ bộ |
| --- | --- | --- |
| Giá quan sát gần nhất | Baseline bắt buộc, phản ánh giá có tính ổn định | y_hat(t+1) = last_observed_price(t) |
| Giá bình quân trượt | Baseline có làm mượt | Bình quân gia quyền giao dịch trong 4 hoặc 8 tuần lịch gần nhất; không có quan sát thì quay về giá gần nhất |
| Ridge Regression | Baseline học máy tuyến tính | StandardScaler cho số và OneHotEncoder cho danh mục; alpha thuộc {0,1; 1; 10; 100} |
| LightGBM Regressor | Mô hình phi tuyến chính để đối sánh | Loss L2; learning_rate thuộc {0,03; 0,05}; num_leaves thuộc {15; 31}; min_child_samples thuộc {20; 50}; tối đa 500 cây, early stopping trên validation |

Ưu tiên công cụ đã có trong repo: pandas, NumPy, scikit-learn, Matplotlib/Seaborn và LightGBM đã xuất hiện trong notebook. Môi trường chạy chính thức cần bổ sung phiên bản LightGBM vào hồ sơ phụ thuộc vì requirements hiện tại chưa liệt kê thư viện này. Notebook là giao diện demo chính; không bắt buộc xây hạ tầng Lakehouse, API, Feature Store hay ứng dụng web mới.

Sử dụng cùng bảng đặc trưng có kiểm soát cho Ridge và LightGBM. Siêu tham số và cửa sổ được chọn trên validation theo WAPE; nếu tương đương thì ưu tiên cấu hình đơn giản. Mô hình ngẫu nhiên chạy các seed 17, 42, 2026; cố định quy tắc tổng hợp kết quả trước khi xem test. Không chọn seed tốt nhất theo test. Không bổ sung loss bất đối xứng hoặc mô hình thứ hai để dự đoán rủi ro trong phạm vi chính.

Đối sánh mở rộng sử dụng 10 phương pháp 2023–2026 ở hồ sơ [4], tách track target-only chung thông tin và track ngoại sinh hợp lệ theo khả năng từng implementation; Moirai2 không được gán khả năng covariates của Moirai1. Toàn bộ 10 phương pháp hiện chưa full-run trên dữ liệu nhóm. Kế hoạch cài, smoke/pilot/full và failure log không được trình bày như kết quả đã hoàn thành. Bản đề xuất residual dùng LightGBM là cách tiếp cận cần kiểm chứng, không được gọi LightGBM là SOTA mới 2023–2026.

## Mục 8. Kịch bản thực nghiệm và tiêu chí đánh giá

### 8.1. Chia tập và chống rò rỉ

Chia theo các tuần đích đầy đủ, dùng chung mốc cho mọi SKU: khoảng 70% tuần đầu cho train, 15% tiếp theo cho validation và 15% cuối cho test. Mốc cụ thể cùng số mẫu được xuất sau khi hoàn thành pipeline, không sao chép số mẫu từ bảng lượng bán cũ. Bảo đảm max(target_week_train) < min(target_week_validation) và max(target_week_validation) < min(target_week_test).

Giao thức chính là dự báo một bước cuốn chiếu: sau khi tuần t kết thúc, được sử dụng giao dịch thực đã quan sát đến t để dự báo t+1; tham số mô hình cố định sau giai đoạn lựa chọn. Vì vậy lịch sử các tuần test đã trôi qua có thể dùng cho dự báo tuần test tiếp theo, nhưng không fit lại mô hình hoặc chỉnh tham số theo nhãn test. Khi chốt cấu hình có thể fit lại trên train + validation và ghi rõ bước này. Không mô tả giao thức này là dự báo toàn bộ nhiều tuần từ một mốc duy nhất.

Nếu đủ nguồn lực, thực hiện ba fold expanding-window trong giai đoạn trước test để kiểm tra độ ổn định theo thời gian. Tập test cuối vẫn khóa và chỉ dùng cho báo cáo cuối theo kế hoạch đã chốt. Không dùng random train_test_split cho kết luận dự báo tương lai.

### 8.2. Độ đo

- MAE = mean(|y − y_hat|): sai số tuyệt đối theo đơn vị tiền gốc.
- RMSE = sqrt(mean((y − y_hat)²)): nhạy với sai số lớn.
- WAPE = 100 × Σ|y − y_hat| / Σ|y|: chỉ số lựa chọn chính; đây là tỷ lệ tổng sai số giá trên tổng giá quan sát, không tự động mang nghĩa tổn thất doanh thu.
- Macro-WAPE theo SKU: tính WAPE từng SKU đủ nhãn rồi lấy trung bình; báo số SKU và phân phối số nhãn/SKU để tránh nhóm đắt tiền che khuất nhóm khác.
- Độ phủ nhãn = số cặp đủ điều kiện dự báo có nhãn quan sát / tổng số cặp đủ điều kiện dự báo. Báo thêm số dự báo thiếu và nguyên nhân.
- Cải thiện so với baseline = 100 × (WAPE_baseline − WAPE_model) / WAPE_baseline khi mẫu số > 0. Không quy đổi cải thiện sai số thành tăng lợi nhuận.

Mọi mô hình được chấm trên cùng tập mẫu; không loại mẫu khó riêng cho từng mô hình để tăng điểm. Có thể báo R² bổ sung nhưng không dùng riêng R² toàn bộ SKU làm bằng chứng mô hình tốt, vì chênh lệch mặt bằng giá giữa SKU có thể rất lớn.

### 8.3. Kịch bản kiểm chứng

| Kịch bản | Nội dung so sánh | Cách diễn giải |
| --- | --- | --- |
| Toàn bộ test | Bốn phương pháp trên cùng tập nhãn quan sát | Có cải thiện thực chất so với giữ nguyên giá không? |
| Theo thời gian/ngành hàng | Sai số theo tháng, ngành hàng và nhóm mức giá | Kết quả tổng thể có che khuất nhóm dự báo kém không? |
| Giá biến động | Tách tuần có thay đổi giá thực so với giá gần nhất vượt ngưỡng xác định từ train | Phân tích lỗi hậu nghiệm; không xem đây là nhóm biết sẵn ở lúc dự báo |
| Lịch sử thưa/dày | Chia theo tần suất có giao dịch trong quá khứ, ngưỡng chọn từ train | Nhãn và độ ổn định khác nhau thế nào? |
| Ablation | Giá quá khứ → thêm giao dịch → thêm lịch/danh mục; thêm đối chứng bỏ snapshot | Nhóm đặc trưng nào có ích, có phụ thuộc quá mạnh vào snapshot không? |
| Độ ổn định | Các fold thời gian trước test, seed đã chốt và thời gian chạy | Cải thiện có nhất quán và phù hợp tài nguyên nhóm không? |

Nếu có điều kiện, ước lượng khoảng tin cậy của chênh lệch sai số bằng bootstrap theo khối tuần, thay vì giả định mọi dòng SKU–tuần độc lập. Chỉ kết luận cải thiện trong phạm vi có bằng chứng. Không so điểm test của nhóm trực tiếp với điểm công bố trên dataset khác để tuyên bố vượt SOTA.

## Mục 9. Sản phẩm dự kiến và phương án ứng dụng

1. Thuyết minh, bảng khảo sát tài liệu và từ điển các bảng/cột thực sự sử dụng.
2. Notebook/script kiểm kê, kiểm tra chất lượng và ETL; log dòng bị loại/cách ly cùng báo cáo trước/sau.
3. Bảng SKU–tuần và các tập modeling giá riêng; cấu hình chia tập và danh sách đặc trưng có nguồn gốc.
4. Notebook baseline và mô hình, bảng kết quả sinh tự động, biểu đồ thực tế–dự báo và phân tích lỗi.
5. Bảng tra cứu minh họa trong notebook: chọn SKU và tuần, xem giá gần nhất, giá dự báo, thay đổi dự kiến và chất lượng lịch sử.
6. Hướng dẫn chạy lại, phiên bản thư viện, seed, checksum dữ liệu và giới hạn áp dụng.

Quy trình sử dụng: người phụ trách dữ liệu chạy kiểm tra → bảng dữ liệu đạt điều kiện được cập nhật → mô hình tạo dự báo → chuyên viên ngành hàng rà soát kết quả. Khi kiểm tra khóa/liên kết hoặc bảo toàn tổng thất bại, pipeline dừng xuất dữ liệu modeling thay vì tiếp tục tạo dự báo. Demo không tự phát cảnh báo tổn thất, không thay đổi giá tại hệ thống bán hàng.

## Mục 10. Kế hoạch thực hiện

| Giai đoạn | Công việc | Đầu ra kiểm tra được |
| --- | --- | --- |
| Tuần 1 | Chốt định nghĩa nhãn/cutoff/phạm vi; xác minh nguồn; khảo sát nghiên cứu trực tiếp về giá | Đề cương và bảng tài liệu có dẫn chứng |
| Tuần 2 | Kiểm kê/schema/khóa/tham chiếu; chuẩn hóa; báo cáo chất lượng | Inventory, rule catalog, log, bảng giao dịch hợp lệ |
| Tuần 3 | Lịch tuần, nhãn, đặc trưng, chia tập; kiểm tra rò rỉ và baseline giá | Modeling table mới, split metadata, baseline tái lập |
| Tuần 4 | Ridge, LightGBM và lựa chọn tham số trên validation | Log cấu hình, kết quả validation |
| Tuần 5 | Khóa kế hoạch; chạy test, ablation, phân tích nhóm và độ ổn định | Bảng kết quả và nhận xét có bằng chứng |
| Tuần 6 | Demo notebook, hoàn thiện báo cáo, đối chiếu số liệu code–báo cáo–slide | Hồ sơ bàn giao và kiểm tra chạy lại |

## Mục 11. Phân công nhiệm vụ dự kiến

| Thành viên | Nhiệm vụ chính | Sản phẩm |
| --- | --- | --- |
| Võ Đình Kiên | Điều phối, thống nhất hợp đồng dữ liệu, tích hợp và tái lập pipeline | Notebook tổng và checklist bàn giao |
| Quách Tuấn Kiệt | Inventory, từ điển, thiết kế quy tắc chất lượng | Rule catalog và báo cáo chất lượng |
| Huỳnh Chí Kiên | Làm sạch, EDA, tổng hợp tuần và kiểm tra bảo toàn | ETL và biểu đồ mô tả dữ liệu |
| Nguyễn Hữu Bảo Lộc | Tài liệu nghiên cứu giá, đối chiếu nguồn và phạm vi so sánh | Bảng khảo sát và trích dẫn |
| Đỗ Văn Lộc | Bối cảnh nghiệp vụ, phạm vi sử dụng và demo bảng tra cứu | Mô tả nghiệp vụ, demo notebook |
| Lê Sỹ Liêm | Chia tập, kiểm tra thời điểm, bộ đánh giá và ablation | Split metadata, metric và bảng kiểm chứng |
| Trần Hồng Lĩnh | Baseline, Ridge/LightGBM, tuning và log mô hình | Notebook mô hình và kết quả sinh tự động |

Phân công giữ tên thành viên theo hồ sơ hiện có và là đề xuất để nhóm xác nhận. Các cặp ETL–đánh giá và mô hình–tài liệu kiểm tra chéo; mọi người đọc lại giới hạn và số liệu trước khi nộp.

## Mục 12. Rủi ro và phương án dự phòng

| Rủi ro | Cách phát hiện | Phương án |
| --- | --- | --- |
| Giá ít thay đổi, baseline đã rất tốt | Đo thay đổi trong train; đối sánh last-price | Báo cáo trung thực; tập trung phân tích điều kiện cải thiện, không thêm nhiệm vụ để che kết quả |
| Dữ liệu mô phỏng hoặc không đại diện thực tế | Kiểm tra metadata, phân phối và quy tắc tạo dữ liệu nếu có | Giới hạn kết luận ở dữ liệu công khai; không tuyên bố hiệu quả triển khai thực tế |
| Tuần không bán, nhãn không quan sát | Độ phủ theo SKU/tuần/ngành hàng | Không tạo nhãn giả; báo độ phủ và thiên lệch chọn mẫu |
| Nhân dòng khi join hoặc dùng lại artifact cũ | Kiểm tra cardinality, khóa và tổng lượng/giá trị | Sinh modeling giá trong phiên bản riêng; không ghi đè dữ liệu lượng bán–rủi ro |
| Rò rỉ tương lai hoặc snapshot danh mục | Kiểm tra target_week, cửa sổ đặc trưng và thời điểm sẵn có | Loại biến tương lai; giả định snapshot nêu rõ và chạy đối chứng |
| Thiếu thời gian/tài nguyên | Theo dõi thời gian chạy và tiến độ | Giảm ngân sách tuning; giữ baseline + Ridge + LightGBM, không thêm Transformer |
| Tài liệu có số liệu không truy nguyên | Đối chiếu bảng báo cáo với file kết quả/log | Chỉ đưa số từ pipeline; xóa hoặc ghi rõ mục tiêu dự kiến đối với số chưa kiểm chứng |

## Mục 13. Tài liệu tham khảo và ghi chú xác minh

[1] fahdelatiby. Electronics Sales Dataset (B.Tech style). Kaggle. https://www.kaggle.com/datasets/fahdelatiby/electronics-sales-dataset-b-tech-style . Dữ liệu dùng trong đề xuất là bản CSV cục bộ của repo; cần xác minh lại giấy phép, nguồn gốc và tiền tệ từ tác giả.

[2] R. J. Hyndman và G. Athanasopoulos. Forecasting: Principles and Practice, 3rd edition. OTexts, 2021. https://otexts.com/fpp3/ . Tham khảo baseline đơn giản và đánh giá dự báo theo thời gian; không trích số liệu thực nghiệm của sách cho bài toán nhóm.

[3] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye và T.-Y. Liu. “LightGBM: A Highly Efficient Gradient Boosting Decision Tree.” Advances in Neural Information Processing Systems 30, 2017. https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html . Đã đối chiếu tên bài/tác giả/năm với trang proceedings; chỉ kế thừa phương pháp, không sao chép kết quả khác dữ liệu.

**Ghi chú biên soạn:** Bố cục tham khảo thuyết minh Nhóm 1 trong repo, đặc biệt cách tách bằng chứng, phạm vi thông tin và kiểm soát dữ liệu. Thông tin hành chính giữ theo hồ sơ Nhóm 5. Không dùng thuyết minh Nhóm 3 để xây dựng bản này. Mục tổng quan nghiên cứu ứng dụng trực tiếp còn cần bổ sung trước bản nộp chính thức; đây không phải một khảo sát SOTA đã hoàn tất.

[4] Nhóm 5. Hồ sơ đối chiếu 10 phương pháp dự báo 2023–2026, chốt 06/11/2026. Tài liệu tổng hợp nội bộ: outputs/reports/sota_price_2023_2026/RELATED_WORK_VA_GAP.md, methods.json và evidence/manifest.json. Đây là chỉ mục đến các nguồn sơ cấp, không thay thế paper gốc; URL, phiên bản, bảng bằng chứng và giới hạn xuất bản được ghi theo từng phương pháp trong hồ sơ.

## Phụ lục. Checklist trước khi chốt bản chính thức

- Xác nhận đề tài, giảng viên, phân công và lịch nộp với nhóm.
- Xác minh metadata/giấy phép/tiền tệ; bổ sung ít nhất ba nghiên cứu ứng dụng dự báo giá phù hợp, dẫn đến trang/bảng bằng chứng.
- Chốt lịch tuần, cohort SKU và quy tắc giao dịch; xuất số mẫu thực tế thay vì dùng số từ artifact cũ.
- Kiểm tra trùng khóa, orphan, số dòng sau join và bảo toàn tổng Quantity/tổng giá trị.
- Kiểm tra nhãn đúng tuần t+1; không forward-fill nhãn; xuất độ phủ tuần có giao dịch.
- Kiểm tra không có biến tương lai; tất cả biến đổi học từ train; ghi rõ giả định snapshot.
- Chốt baseline, ngân sách tuning, seed và nhóm phân tích trước khi mở kết quả test cuối.
- Sinh bảng kết quả từ code; thống nhất các số ở notebook, báo cáo và slide; kiểm tra chạy lại trên môi trường đã ghi phiên bản.