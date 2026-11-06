# RELATED WORK 2023–2026 VÀ THIẾT KẾ THỰC NGHIỆM

## Dự báo giá bán thực tế theo SKU–tuần trong bán lẻ điện máy

**Ngày chốt khảo sát: 06/11/2026.** Đối tượng: Nhóm 5 – DS317.R11. Đây là khảo sát có kiểm tra nguồn và đề xuất gap, **không phải báo cáo đã cài/chạy đủ 10 phương pháp**. Tất cả 10 phương pháp hiện có trạng thái NOT_RUN trên bộ dữ liệu nhóm. Bảng số công bố thuộc paper/release tác giả, không phải kết quả của nhóm.

Hồ sơ đi kèm: methods.json chứa 10 hồ sơ phương pháp; evidence/ lưu nội dung nguồn, bảng HTML tách thành hàng/cột, URL, thời điểm tải và checksum. File Excel có bảng tổng quan, năng lực, kết quả công bố, trạng thái chạy và thiết kế benchmark. Chưa thể gọi đây là systematic review đầy đủ mọi nghiên cứu retail price trên thế giới.

## 1. Kết luận điều hành: nhóm nên làm gì?

Đề xuất tập trung vào **dự báo giá giao dịch SKU–tuần khi lịch sử ngắn/thưa và phần lớn giá ít đổi**, so sánh học có giám sát với foundation models mới trong điều kiện thông tin sẵn có thực tế. Không mở lại dự báo nhu cầu hoặc phân loại rủi ro.

**Câu hỏi chính:** Với cùng lịch sử và cùng nhãn giá thực quan sát, các mô hình mới 2023–2026 có cải thiện được so với giữ nguyên giá gần nhất không? Nếu có, cải thiện đến từ biến ngoại sinh, dữ liệu tiền huấn luyện, cách biểu diễn giá hay chỉ từ khác biệt giao thức đánh giá?

**Phương án cải tiến có thể kiểm chứng:** price-anchor residual forecasting + missingness/recency-aware covariates + regularized blending với last-price. Đây là kết hợp các ý tưởng đã biết để kiểm tra trong bối cảnh cụ thể, không tuyên bố phát minh toàn bộ kỹ thuật.

**Không lấy “tick hết” làm bằng chứng mới.** Một bảng nhiều dấu tick chỉ chứng minh độ phủ tính năng trong phạm vi tiêu chí tự chọn. Nó chưa chứng minh mô hình tốt hơn, mới về thuật toán, có ích về nghiệp vụ hoặc nghiên cứu khác không làm. Dòng của nhóm phải ghi PLANNED trước khi có code/log/kết quả; không tick như tính năng đã hoàn tất.

## 2. Ranh giới bài toán và tiêu chí chọn nguồn

### 2.1. Bài toán cần giữ cố định

Tại cuối tuần t, dự báo duy nhất giá thực tế bình quân gia quyền của SKU i trong tuần t+1:

**y(i,t+1) = Σ Quantity × ActualSellingPrice / Σ Quantity**, tính trên các giao dịch completed hợp lệ trong tuần đích.

Không dự báo tổng tiền đơn, lượng bán, giá niêm yết tĩnh hay giá nên tối ưu. Tuần không bán không quan sát được nhãn. Không được forward-fill nhãn rồi báo đó là giá thật.

### 2.2. Ba mức liên quan cần phân biệt

| Mức | Điều kiện | Vai trò trong hồ sơ |
| --- | --- | --- |
| A – trực tiếp | Dự báo giá giao dịch/giá bán sản phẩm bán lẻ theo thời gian, đặc biệt SKU điện máy | Cần nghiên cứu ứng dụng trực tiếp để khẳng định novelty theo domain; hiện chưa xác minh đủ 7–10 bài mức A có code công khai |
| B – phương pháp phù hợp | Dự báo chuỗi với target giá, history covariates, dữ liệu ngắn/thưa hoặc panel; có code và có thể adaptation | 10 phương pháp được chọn chủ yếu ở mức B. TimeXer có benchmark giá điện nhưng không phải giá điện máy |
| C – lĩnh vực lân cận | Retail demand, price index, định giá động, stock/crypto/commodity price | Chỉ làm bối cảnh/nguồn kỹ thuật; không mạo nhận là cùng task |

M5/Rossmann/Favorita trong paper thường dự báo sales/demand. “Có retail benchmark” không đồng nghĩa “đã dự báo giá bán”. Đây là điểm cần nói rõ nếu đưa bảng related work vào thuyết minh.

### 2.3. Phạm vi năm và trạng thái xuất bản

Các phương pháp chính đều có nguồn công bố/release từ 2023–2026. Ghi cả năm preprint, năm venue và phiên bản thực tế. Không gọi tất cả là peer-reviewed: TimesFM-3 có release chính thức 31/08/2026 nhưng chưa xác minh paper riêng; TiDE/Chronos-2/Moirai2/TabPFN-TS được trích theo arXiv nếu chưa xác minh venue khác. TiRex-2 được repo tác giả công bố accepted NeurIPS 2026, không suy rằng proceedings đã xuất bản tại thời điểm khảo sát.

PatchTST là ICLR 2023 nhưng preprint 2022, nên không đưa vào 10 phương pháp chính để tránh hiểu lầm nếu nhóm muốn mọi first release ≥2023. TFT (2021), LightGBM (2017), Ridge và last-price vẫn phải dùng làm baseline khi phù hợp; baseline không cần mới để là đối chứng hợp lệ.

### 2.4. Cách tra cứu và sàng lọc đã thực hiện

Đọc nguồn arXiv full HTML/abstract, official GitHub README, model cards Hugging Face và Google Research release. Truy vấn Crossref theo tiêu đề với cụm “retail price forecasting machine learning”, “e-commerce product price prediction time series” và lọc ngày 2023-01-01 đến 2026-11-06. Tìm theo trích dẫn/code release để cập nhật Chronos-2, Moirai2, TimesFM3, TiRex2 và TabPFN-TS.

Đây là targeted review, không có PRISMA flow hoặc tuyên bố đã bao phủ Scopus/WoS. Các DOI metadata chỉ xác minh danh tính, không chứng minh chất lượng thực nghiệm hay khả năng tái lập.

| Nguồn gần domain đã tìm | Kết quả sàng lọc |
| --- | --- |
| E-Commerce price index prediction with time series mining and automated machine learning, DOI 10.1177/18747655241301198, 2024 | Crossref có metadata; truy cập full source thất bại trong phiên khảo sát. Target là price index theo tiêu đề, chưa chứng minh SKU selling price hoặc code. Không tính vào 10 baseline có thể tái lập |
| Research on Dynamic Price Prediction of E-commerce Based on Time Series Modeling, DOI 10.38007/IJBMET.2026.070105 | Trang publisher truy cập được nhưng abstract tập trung cả chọn vị trí kho/AHP/LINGO; chưa xác minh dataset giá, split thời gian và code. Không chọn chỉ vì tiêu đề có đúng từ khóa |
| TSMixer M5; Chronos-2 Rossmann | Có retail nhưng target sales. Chọn phương pháp vì relevance kỹ thuật, không viện dẫn như bài dự báo actual selling price |

Chưa tìm đủ công trình trực tiếp trong lần tra cứu này **không có nghĩa chưa ai làm**. Cần bổ sung tìm kiếm theo chuỗi “transaction price forecasting”, “retail SKU price time series”, “e-commerce price dynamics”, “markdown price forecasting”, “electronics selling price prediction”, và forward/backward citations trước khi tuyên bố novelty theo domain.

## 3. Mười phương pháp được chọn

| ID | Phương pháp | Năm/nguồn | Họ mô hình | Lý do đưa vào |
| --- | --- | --- | --- | --- |
| M01 | TiDE | 2023, arXiv; v5 2024 | MLP encoder–decoder supervised | Đối chứng covariates không cần attention |
| M02 | TSMixer | TMLR 2023 | MLP time/feature mixing | Retail auxiliary evidence, nhưng official Extended còn thiếu |
| M03 | iTransformer | ICLR 2024; preprint 2023 | Variate-attention supervised | Đối chứng modeling quan hệ giữa biến |
| M04 | TimeMixer | ICLR 2024 | Multiscale MLP supervised | Đối chứng trend/seasonality nhiều thang |
| M05 | TimeXer | NeurIPS 2024 | Endogenous/exogenous Transformer supervised | Gần bài toán một target giá + history ngoại sinh |
| M06 | Chronos-2 | arXiv/release 2025 | Foundation, group attention | Zero-shot covariates + quantiles, checkpoint 120M |
| M07 | Moirai 2.0 | Release/paper 2025; v3 2026 | Foundation decoder-only | Nhỏ 11.4M, missing-aware, quantiles; không covariates |
| M08 | TabPFN-TS | Paper 2025; revision 2026 | Tabular foundation adaptation | Lịch sử ngắn, feature-based; phải pin v2/v3.5 |
| M09 | TimesFM-3 | Google release 08/2026 | Multivariate foundation Transformer | Đối chứng hiện tại 2026, past/future covariates |
| M10 | TiRex-2 | arXiv 07/2026; accepted theo repo | Recurrent xLSTM foundation | Đối chứng recurrent 2026, covariates, quantiles |

Các nguồn chứng minh chúng là phương pháp tiên tiến/đối chứng hiện đại trong forecasting; không đủ để gọi cả 10 là “SOTA giá điện máy hiện tại”. SOTA luôn phải gắn task, dataset, metric, giao thức và thời điểm.

## 4. Ma trận năng lực: tick có điều kiện, không tick cảm tính

Ký hiệu: **✓** có bằng chứng; **—** không hỗ trợ trong bản được nêu; **△** phụ thuộc phiên bản/adapter hoặc hỗ trợ một phần; **?** chưa xác minh. Đánh giá bản gốc/official path, không dùng tính năng của thư viện port để tự nâng năng lực paper gốc.

| Phương pháp | Past covariates | Future-known covariates | Static metadata | Cross-variate | Native uncertainty | Zero-shot pretrained |
| --- | --- | --- | --- | --- | --- | --- |
| TiDE | △ | ✓ global dynamic | △ paper có, code thiếu | △ | △ | — |
| TSMixer | △ | △ Extended | △ Extended chưa có official code | ✓ | △ | — |
| iTransformer | △ biến đồng cấp | — gốc | △ extension | ✓ | △ extension | — |
| TimeMixer | △ | △ temporal features | ? | △ config | △ | — |
| TimeXer | ✓ | △ kiểm tra path/config | ? | ✓ | △ | — |
| Chronos-2 | ✓ | ✓ | △ | ✓ | ✓ | ✓ |
| Moirai 2.0 | — | — | — | — | ✓ | ✓ |
| TabPFN-TS | △ lag adaptation | ✓ | △ | △ | ✓ | ✓ |
| TimesFM-3 | ✓ | ✓ | ? | ✓ | ✓ | ✓ |
| TiRex-2 | ✓ | ✓ | ? | ✓ | ✓ | ✓ |

**Các phát hiện phải giữ trong related work:**

1. TiDE research code nói không hỗ trợ static attributes, dù paper tổng quát có. Không được tick “official reproduction full static support”.
2. TSMixer repo còn đánh dấu Extended TBD. Không thể lấy kết quả TSMixer-Ext rồi cài basic và nói đã tái lập.
3. Moirai 2.0 Section 6 nói rõ đã bỏ multivariate/covariates; không được kế thừa tick từ Moirai 1.0 vì cùng tên họ.
4. iTransformer probabilistic/static có trong extension GluonTS theo README; không phải mặc định bản point gốc.
5. TabPFN-TS latest mặc định backbone 3.5, khác paper v2. Pin checkpoint và gọi tên đúng.
6. TimesFM-3 weights phi thương mại; code Apache không làm weights thành Apache. Tương tự Moirai2 weights CC-BY-NC-4.0.
7. TiRex-2 streaming/fine-tuning PRO không mặc định là chức năng code mở đã chạy. Tuyên bố causality trong paper là thuộc tính kiến trúc cụ thể, không chứng minh các model khác rò rỉ nhãn trong benchmark của nhóm.

## 5. Bằng chứng kết quả công bố: so đúng ngữ cảnh

| Nguồn | Dữ liệu/giao thức | Số liệu đã đối chiếu | Không được suy ra |
| --- | --- | --- | --- |
| TiDE Table 2 | Traffic, horizon 96 | TiDE MSE 0.336/MAE 0.253; PatchTST/64 0.360/0.249 | TiDE tốt hơn mọi metric hoặc MAE tiền tệ bằng 0.253 |
| TSMixer Table 4/5 | M5 retail demand | Basic không auxiliary WRMSSE 0.737±0.033; Extended đủ static/future 0.640±0.013; TFT 0.670±0.020 | Dự báo giá SKU đã đạt WRMSSE này hoặc official Extended code đầy đủ |
| iTransformer Table 1 | Lookback 96, ECL trung bình horizon | MSE 0.178, MAE 0.270 | Mô hình tối ưu cho chuỗi 130 tuần, H=1 |
| TimeMixer Table 2 | Weather, input 96, trung bình horizon 96/192/336/720 | MSE/MAE 0.240/0.271; PatchTST 0.265/0.285 | Đây là điểm chuẩn hóa thời tiết, không phải sai số giá bán |
| TimeXer Table 2 | EPF NP, input 168 giờ, horizon 24 giờ | TimeXer MSE/MAE 0.236/0.268; iTransformer 0.265/0.300 | Giá điện theo giờ giống giá điện máy theo tuần |
| Chronos-2 Table 3 | fev-bench, SQL-based comparison | Avg win rate 90.7%, skill score 47.3%, median runtime 3.6s | WAPE = 47.3%, 3.6 giây trên máy nhóm hoặc vẫn số 1 cuối 2026 |
| Moirai2 Table 1 | GIFT-Eval aggregate | 11.4M: MASE 0.728, CRPS 0.516; large 305M 0.743/0.530 | Mô hình lớn hơn luôn tốt hơn; so trực tiếp với MASE fev-bench |
| TiRex2 Table 1 | Ablation fev-bench | Full MASE 1.527±0.006; future-known subset 0.990±0.007 | Thua Moirai vì 1.527 > 0.728 ở benchmark khác |
| TimesFM3 release | GIFT-Eval/FEV-Bench/TIME, average-rank plots | Có tuyên bố/biểu đồ tác giả; không chép số chính xác khi nguồn chỉ có hình | Điểm nhóm hoặc independent reproduction |
| TabPFN-TS paper v4 | GIFT-Eval, covariate-informed fev-bench | Có kiểm chứng và limitation Section 6; không gộp số latest README backbone 3.5 | Điểm v2 chính là điểm 3.5 |

Các bảng nguồn tách hàng/cột được lưu để tiếp tục đối chiếu. Không điền một số đẹp chỉ để đủ mọi dòng. Khi hoàn thiện literature table cho nộp chính thức, chọn số theo đúng mục tiêu và đối chiếu hàng/cột ở full paper, không lấy trung bình số khác chuẩn hóa.

## 6. Hồ sơ chuyên sâu và mức sẵn sàng tái lập

Mười hồ sơ trong methods.json và các sheet Excel có các trường: danh tính/phiên bản, paper, official code, architecture, chế độ học, original task, kết quả có bằng chứng, covariates, static/cross-variate, uncertainty, missingness, license, môi trường cài, adapter dữ liệu nhóm, strengths/limitations, ưu tiên và run status.

### 6.1. Nhóm supervised M01–M05

Khó khăn không chỉ là pip install. Official scripts thường kỳ vọng wide regular series, đầu ra nhiều biến, thời gian dài, nhãn đầy đủ. Dữ liệu nhóm là panel SKU, giá có quan sát khi bán và chỉ dự báo một target. Phải xác định rõ:

- Tensor [batch SKU-window, lịch tuần, variables] hay wide [time, SKU]? Hai thiết kế không tương đương. Không biến mỗi SKU thành biến mà bỏ qua vòng đời/thiếu quan sát rồi kết luận cross-SKU learning có ích.
- Global model có thể học cửa sổ nhiều SKU chung tham số, nhưng không tự đồng nghĩa các SKU trao đổi thông tin qua attention.
- Nếu dùng history qty/discount làm đầu vào, không thêm loss dự báo qty. Với implementation bắt buộc output nhiều kênh, chỉ lấy price channel và masked loss cho nhãn giá; ghi đây là adaptation.
- Context 8/16/32 tuần, H=1, batch 16/32 là khởi điểm nghiên cứu, không phải cấu hình tối ưu đã xác nhận. Validation chọn cấu hình, không thay đổi sau khi nhìn test.
- Tuning lịch tuần ngắn phải bỏ context quá dài làm không còn đủ cửa sổ train. Dùng masked loss cho target thiếu hoặc chỉ train các cửa sổ có nhãn đúng tuần t+1, tuyệt đối không đổi thành “giá lần bán kế tiếp”.

TSMixer-Ext thiếu official code là rào cản thực sự. Lựa chọn minh bạch: chạy TSMixer basic và ghi đúng giới hạn; hoặc tự cài Extended theo paper có unit tests và đối chiếu, ghi adapted implementation. Không tick “reproduced official Ext” khi chưa làm.

### 6.2. Foundation M06–M10

Không cần pretrain lại từ đầu. “Cài và chạy phương pháp” ở đây là khóa code/checkpoint → tải weights → kiểm tra API/missingness → inference zero-shot trên các origin của nhóm → chấm điểm chung. Fine-tune nếu làm là nhánh độc lập, có train/validation riêng và chi phí riêng.

Với models có quantiles, lấy median cho MAE là lựa chọn hợp lý; nếu RMSE/WAPE dùng point mean/median cần ghi và giữ nhất quán. Native quantiles có thể không được calibration đúng trên price panel, vì vậy pinball/WIS/coverage là kiểm chứng, không một dấu tick đủ chứng minh.

### 6.3. Phân biệt các trạng thái thực thi

| Trạng thái | Bằng chứng tối thiểu |
| --- | --- |
| SOURCE_VERIFIED | Paper/release + code URL đã đọc và có bản lưu |
| INSTALLED | Môi trường riêng, version/commit, import test, pip check log |
| SMOKE_PASSED | Inference/train nhỏ trên synthetic, đúng shape, hữu hạn, chỉ dùng cutoff hợp lệ |
| PILOT_PASSED | Subset SKU từ train/validation, log prediction keys và thời gian |
| FULL_RUN | Đủ toàn bộ tập đánh giá đã khóa, có predictions và run metadata |
| REPRODUCED_PAPER | Chạy đúng dataset/giao thức paper và kiểm tra sai lệch, khác FULL_RUN trên dữ liệu nhóm |

Hiện các model ở SOURCE_VERIFIED/NOT_RUN trên dữ liệu nhóm; chưa có INSTALLED/SMOKE/FULL_RUN. Một lần import thành công không phải đã thực nghiệm đầy đủ.

## 7. Gap nào còn đứng vững sau khi đọc nguồn mới?

### 7.1. Các gap phải loại

- “Chưa có model dùng ngoại sinh”: sai với TimeXer, Chronos2, TimesFM3, TiRex2.
- “Chưa có model dự báo xác suất”: sai với foundation models quantile.
- “Chưa có model xử lý missing”: sai nếu nói chung; Moirai2 có missing-aware patch embedding.
- “Kết hợp DQ + dashboard là cải tiến thuật toán”: không; đó là quy trình/hệ thống, vẫn có giá trị nhưng loại đóng góp khác.
- “Không có bài nào dùng đúng dataset Kaggle này nên mới”: chưa đủ; novelty theo dataset không tự thành đóng góp khoa học.
- “Model mình tick static + exogenous + quantile + explainability nên hơn”: chưa có bằng chứng hiệu năng, không so đồng cấp feature của phương pháp và quy trình nhóm.

### 7.2. Gap ứng viên và bằng chứng cần bổ sung

| Gap ứng viên | Bằng chứng hiện có | Cần kiểm chứng thêm | Mức tuyên bố an toàn |
| --- | --- | --- | --- |
| External validity cho actual transaction price SKU-week, lịch sử ngắn/thưa | Nguồn được đọc chủ yếu generic TS, retail demand hoặc EPF | Full domain review và dataset card; xác định price dynamics trong dữ liệu nhóm | Khoảng trống đánh giá trong các nguồn đã khảo sát, không tuyên bố toàn literature |
| Điểm aggregate che performance trên tuần price-change | Baseline thăm dò trước cho last-price WAPE thấp; các paper không được xác minh đánh giá đúng cohort này | Chạy lại last-price trên pipeline sạch, đo stability ở train, phân nhóm hậu nghiệm trên test | Câu hỏi thực nghiệm phù hợp, không chứng minh chưa ai từng nghiên cứu regime |
| Missingness do không bán và label observability | Nhãn giá vắng khi qty=0; missing embedding chung không giải quyết hết selection bias | Báo độ phủ, kiểm tra label policy và no-sale gap; tránh target imputation | Gap giao thức trong bài toán nhóm, không nhận diện price thực tuần không bán |
| Availability-aware exogenous features | API model hỗ trợ exogenous, nhưng dữ liệu CSV không chứng minh lịch khuyến mãi biết trước | Feature availability ledger, unknown-future excluded; ablation history-only vs future-known calendar | Đóng góp về thực nghiệm/độ tin cậy, không nói kiến trúc model khác gây leakage |
| Accuracy–cost tradeoff giữa supervised và 2026 TSFM | Model size/API/constraints khác nhau; chưa có điểm trên nhóm | Same origins, tuning budget rõ, latency/RAM/download/load/inference riêng | Benchmark ứng dụng có ích, chưa phải cải tiến thuật toán |

**Phát biểu gap đề xuất:** “Trong các nguồn đã khảo sát, còn thiếu một đối sánh đồng nhất giữa supervised forecasters và các foundation models mới cho giá giao dịch SKU–tuần có lịch sử ngắn, nhãn quan sát theo giao dịch và thông tin ngoại sinh chỉ biết ở cutoff; đặc biệt cần kiểm chứng mức cải thiện so với last-price trên cả tuần ổn định và tuần biến động.”

Đây là **gap đánh giá có điều kiện**, không phải kết luận chắc chắn rằng chưa công trình nào từng làm. Muốn nâng thành novelty cần hoàn thiện domain search và có kết quả thực nghiệm hỗ trợ.

## 8. Một hướng cải tiến cụ thể, vẫn chỉ một nhiệm vụ

### 8.1. Price-anchor residual regression

Chọn a(i,t) là giá quan sát gần nhất ≤t, dương. Thay vì học trực tiếp y có mặt bằng rất khác giữa SKU, học:

**r(i,t+1) = log[y(i,t+1) / a(i,t)]**.

Mô hình trả r_hat, khôi phục **y_hat = a × exp(r_hat)**. r=0 đúng là last-price baseline. Giá trị này không phải classifier “có đổi giá hay không”, nên vẫn một bài toán regression.

Feature gồm residual/giá quá khứ, quantity và discount quá khứ, recency từ lần có giá, số tuần có quan sát và known calendar. Mask/recency thuộc đầu vào; nhãn không quan sát vẫn không dùng chấm điểm. Fit preprocessing trên train, tránh giá tham chiếu dựa vào tương lai.

Có thể thử hai cơ chế thay thế (không cộng cả hai rồi không biết phần nào có ích): regularization đưa residual về 0, hoặc blending **y_final = λ × a + (1−λ) × y_hat**, λ∈{0, 0.25, 0.5, 0.75, 1} chọn toàn cục trên validation. Blending là kỹ thuật đã biết, không tuyên bố mới.

Nếu muốn λ thay đổi theo recency/độ thưa, phải dùng đặc trưng có sẵn tại t và dự báo out-of-fold từ train để fit gate; không học gate bằng nhãn test hoặc nhóm price-change tương lai. Với thời gian đồ án, ưu tiên λ toàn cục trước.

### 8.2. Giả thuyết và ablation bắt buộc

| Giả thuyết | Thí nghiệm | Điều kiện bác bỏ |
| --- | --- | --- |
| H1: anchor/residual giúp giữa SKU có mức giá khác nhau | Cùng learner, cùng features/budget: raw price vs log-price vs log-ratio | Không cải thiện validation/backtest hoặc chỉ tăng điểm aggregate do vài SKU |
| H2: observability/recency giúp lịch sử thưa | Bỏ/thêm mask, recency và tỷ lệ tuần có giá | Không cải thiện nhóm sparse và interval/point errors |
| H3: ngoại sinh quá khứ có ích | Target-only vs +qty/discount≤t vs +calendar | Không hơn target-only hoặc gains mất sau availability audit |
| H4: shrink/blend bảo vệ tuần ổn định mà không phá tuần đổi giá | Base model vs validation-selected λ, so với last-price | Chỉ copy baseline, không tăng ích trên nhóm change hoặc giảm chất lượng tổng |
| H5: cách đơn giản cạnh tranh TSFM mới | Proposed vs best traditional vs best supervised vs best foundation | Không thắng vẫn báo điều kiện và cost; không kết luận thuật toán hơn SOTA |

Nếu kết quả cho thấy foundation model mới đã giải quyết tốt vấn đề và proposal không hơn, đóng góp còn lại là benchmark và phân tích điều kiện; không được viết gap thành “đã giải quyết” bằng cách đổi tiêu chí sau test.

## 9. Bảng related work kiểu tick: thiết kế đúng hai tầng

### 9.1. Tầng phương pháp

Dùng ma trận năng lực ở Mục 4. Không thêm DQ gate hay dashboard vào đó để biến kiến trúc khác thành nhiều dấu trống giả tạo. Định nghĩa tiêu chí trước, nêu version/implementation.

### 9.2. Tầng nghiên cứu ứng dụng của nhóm

| Hạng mục cần chứng minh | 10 nguồn hiện tại | Nhóm – mục tiêu | Bằng chứng mới được tick |
| --- | --- | --- | --- |
| Đúng target actual SKU-week price của nhóm | Chưa xác minh ở 10 nguồn | PLANNED | Pipeline nhãn và từ điển, log đối chiếu giao dịch |
| Baseline persistence mạnh | Không kết luận chung mọi paper | PLANNED | Last-price same origins, cùng cohort |
| Nhãn quan sát khi có giao dịch, không impute truth | Không mặc định paper nào cũng thiếu | PLANNED | Observation mask + coverage + target-week tests |
| Availability-aware covariates | Các model hỗ trợ khác nhau, không đồng nghĩa đã audit dữ liệu nhóm | PLANNED | Feature ledger và cutoff assertions |
| Rolling-origin benchmark 10 phương pháp | Chưa có trên repo nhóm | PLANNED | Prediction files + hash + model/config metadata |
| Stable/change và sparse/dense analysis | Chưa xác minh đúng cohort này | PLANNED | Threshold từ train; per-scenario errors có mẫu số |
| Uncertainty được kiểm chứng | Một số có quantiles; calibrated trên nhóm chưa biết | OPTIONAL/PLANNED | Pinball/WIS/coverage-width; không suy bảo đảm finite-sample dưới drift |
| Cost/accuracy và lỗi chạy được báo | Số published thuộc phần cứng khác | PLANNED | Wall time, RAM/VRAM, failures, model load/download tách riêng |
| Residual/anchor/recency ablation | Không tuyên bố chưa ai làm kỹ thuật | PLANNED | Bảng controlled ablation và code |

Khi tất cả tiêu chí đã có bằng chứng, dòng nhóm có thể tick đủ **trong benchmark ứng dụng này**, không tự thành “vượt mọi phương pháp trên mọi mặt”. Những feature không liên quan câu hỏi chính không cần tick.

## 10. Benchmark chung: thiết kế để cài và chạy thật

### 10.1. Kiểm tra dữ liệu trước mọi model

- Raw data checksum, schema/kiểu, trạng thái đơn normalize complete/completed và canceled/cancelled; key uniqueness và conflict quarantine.
- Many-to-one joins có validate, kiểm tra orphan; số dòng, tổng Quantity và tổng tiền không bị nhân khi nối.
- Lịch tuần chuẩn và tuần biên; cohort tạo từ quá khứ, không cắt bằng ngày bán cuối nhìn toàn tương lai.
- Giá quan sát = revenue/qty; qty=0 → target missing, không target=0; nhãn đúng target_week=origin_week+7 ngày.
- Model input không chứa FutureSales, cov_fwd, risk, y_qty hoặc price/discount tương lai. Static snapshot được ghi giả định và kiểm chứng bỏ snapshot.
- Split theo target_week với mốc chung mọi SKU; fit scalers/imputers trên train. Mỗi cặp khóa duy nhất.

### 10.2. Chia tập và hai track công bằng

Khoảng 70/15/15 theo tuần đích đầy đủ; ba expanding-window folds trước test để chọn tham số. H=1 là bài chính; không thêm H=4 rồi đánh đồng cùng bài nếu chưa định nghĩa lại nhãn. Lịch sử test đã trôi qua được cập nhật cho tuần tiếp theo, weights/siêu tham số không thay bằng kết quả test.

**Track A – target-only common-information:** 10 model cùng history giá và cutoff, cùng origins. Dùng để so kiến trúc/pretraining trong phạm vi thông tin chung. Các model không hỗ trợ missing giống nhau có thể có hai phân tích phụ: causal common imputation và native-missing (chỉ model có hỗ trợ). Không gọi native support là so kiến trúc thuần túy khi preprocessing khác.

**Track B – best-supported valid covariates:** cho model dùng history qty/discount, known calendar nếu API hỗ trợ. Moirai2 N/A ở track B, vẫn có điểm track A. Không ép model không hỗ trợ nhận feature giả rồi so. Có thêm so sánh paired feature ablation trong từng model để thấy lợi ích feature, không gán mọi gain cho kiến trúc.

**Baselines ngoài 10 nguồn:** last-price, rolling weighted price, Ridge, LightGBM. Chúng không cần thỏa năm ≥2023. Thiếu last-price thì benchmark dễ chỉ chứng minh model phức tạp thắng một baseline yếu.

### 10.3. Missingness và đầu ra chuẩn

Adapter tạo prediction ở origin cho SKU có ít nhất một giá lịch sử dương; chấm điểm khi tuần đích có nhãn. Mọi model phải nộp cùng key set. Nếu crash hoặc thiếu key, báo failure/coverage, không silently bỏ các dòng đó để thắng. Summary common cohort cần công bố rõ dòng nào bị loại và lý do.

Schema prediction: model_id, run_id, track, seed, sku_id, origin_week, target_week, prediction, q10/q50/q90 nếu hỗ trợ; y_true/observation flag nằm trong evaluator, không truyền vào adapter inference. CSV metrics không thay cho raw predictions.

Schema run metadata: git commit upstream + adapter, checkpoint ID/revision/hash, model/package version, data hash, split hash, context/horizon, features, preprocessing, hyperparameters, seed, train/validation dates, timestamps, hardware và failure reason.

### 10.4. Metrics và độ tin cậy

Point: MAE, RMSE, WAPE, macro-WAPE/SKU, improvement vs last-price, số mẫu/SKU và nhãn coverage. Không so raw MSE của price scales khác nhau. R² chỉ phụ vì mức giá giữa SKU dễ làm chỉ số đẹp.

Probabilistic subset: pinball loss, WIS khi đủ quantile levels, empirical 80% coverage và interval width. Native quantiles được đánh giá không phải mặc định calibrated. Nếu thêm conformal thì dùng calibration split riêng trước test và nêu giả định temporal dependence; không tuyên bố coverage bảo đảm dưới mọi drift.

Uncertainty kết quả: bootstrap paired loss theo block tuần, giữ các SKU cùng tuần trong block; chỉ định độ dài block trên validation. Kiểm tra nhiều so sánh cần điều chỉnh/thận trọng, không chọn một p-value đẹp trong hàng chục scenario. Nếu không làm inference thống kê thì mô tả descriptive, không nói significant.

Price-change subgroup dùng relative difference so với giá gần nhất, threshold xác định train. Đây là hậu nghiệm sau có y_test, không input/gating có sẵn lúc forecast. Sparse/dense dùng history quan sát trước cutoff, không toàn bộ đời SKU tương lai.

### 10.5. Budget và thứ tự chạy

1. Smoke trên synthetic và vài cửa sổ train: shape, finite values, cutoff, quantile ordering nếu có.
2. Pilot 20 SKU chọn bằng tiêu chí train (mức giá/ngành hàng/độ thưa), dùng validation, không rút test để tune.
3. Supervised: context {8,16,32}, tối đa 6 cấu hình/model trong pilot; full train tối đa 30 epochs, patience 5, seed 17/42/2026. Đây là budget đề xuất cần lock trước test, không phải hứa đủ tối ưu như paper.
4. Foundation: zero-shot context {16,32,64} nếu lịch sử cho phép, native checkpoint cố định, batch điều chỉnh theo RAM. Không dùng 3 seed giả cho model inference deterministic.
5. Khóa dữ liệu/config, chạy full test; tách các configuration run nếu có fine-tuning.
6. Chạy ablation trên learner được chọn theo validation; có proposed point model duy nhất, không thêm classification head.

Một run = model/config/track/seed/fold, không phải cả benchmark. 10 models × 2 tracks × nhiều fold/config sẽ thành hàng trăm run; việc cài đủ thư viện không giải quyết chi phí experiment. RAM/GPU giờ không biết trước, phải pilot đo, không tự hứa “mọi model <3 phút”.

### 10.6. Môi trường cài đặt và giới hạn máy hiện tại

Đã kiểm tra: Windows, Python 3.11.2, PyTorch 2.2.0+cpu, CUDA=False. Có TensorFlow, lightgbm; chưa có chronos/timesfm/uni2ts/tabpfn_time_series/tirex/neuralforecast. Việc thư viện tồn tại không chứng minh version tương thích hoặc model đã chạy.

Tạo env độc lập cho TensorFlow research models, PyTorch supervised, Chronos2, uni2ts, TimesFM3, TabPFN-TS và TiRex2. Không pip upgrade toàn bộ vào env hiện tại. Khóa dependencies từ upstream đã chọn rồi chạy import + pip check; lưu requirements lock theo mỗi env. Khi dùng bash script, Linux/Colab thường hợp hơn Windows; cần test chứ không mặc định CPU không chạy được.

Các package upstream chưa được xác nhận đang dùng trong codebase dự án thì chỉ đưa vào kế hoạch cài, không thêm import model giả vào pipeline đang hoạt động. Các cổng cần tải weights/licensing/user account phải giải quyết minh bạch. TabPFN default cloud không được chạy ngầm: cần LOCAL và chấp thuận license, tránh vô tình truyền dữ liệu ra API.

## 11. Kế hoạch công việc có thể giao ngay

| Gói việc | Việc cần làm | Điều kiện hoàn thành |
| --- | --- | --- |
| W1 – Domain literature | Tìm thêm nghiên cứu retail transaction price; đọc full paper, audit split/code | Bảng include/exclude có nguồn và bằng chứng, không chỉ title matching |
| W2 – Data contract | Tạo modeling giá mới và observation/cohort policy | Assertion keys/joins/target-week/cutoff, data quality log và hashes |
| W3 – Evaluator | Metrics, scenarios, prediction contract, failures/cost | Synthetic tests và replay từ prediction files |
| W4 – Baseline | Last-price, rolling, Ridge, LightGBM | Clean baseline điểm validation, xác định có signal đáng học |
| W5 – 5 supervised | Official code hoặc adaptation ghi rõ, masked target/output | Install/smoke/pilot/full logs riêng, không nhận basic là Extended |
| W6 – 5 foundation | Pin weights và API; target-only rồi valid features | Cùng prediction keys, checkpoint revisions, licenses và cost |
| W7 – Proposed | Anchor residual, recency, blending; ablation | So raw/log/residual và feature groups có controlled budgets |
| W8 – Tổng hợp | Export related work và empirical tables từ source/log | Dòng proposed chỉ tick khi có evidence, không nhập tay điểm đẹp |

Ưu tiên P1: TimeXer, Chronos2, Moirai2, TabPFN-TS, TimesFM3, TiRex2; P2: TiDE, TSMixer, iTransformer, TimeMixer. Đề xuất này chỉ là thứ tự thực hiện, không phải bỏ yêu cầu chạy đủ 10. Nếu một phương pháp không tái lập được, phải giữ failure row và giải thích, hoặc thay bằng nguồn khác theo tiêu chí đã chốt; không âm thầm loại model yếu/mạnh sau test.

## 12. Kết luận có thể dùng khi trao đổi với cô

“Nhóm giữ một bài toán dự báo giá bán thực tế SKU–tuần. Qua khảo sát các phương pháp 2023–2026, hỗ trợ ngoại sinh và dự báo phân vị đã có ở nhiều mô hình mới nên nhóm không xem đó là gap riêng. Nhóm tập trung kiểm chứng khả năng dự báo giá giao dịch lịch sử ngắn/thưa, với nhãn chỉ quan sát khi có giao dịch và thông tin đầu vào thực sự sẵn có. Nhóm đối sánh 10 phương pháp hiện đại với persistence/ML baselines, phân tích tuần ổn định và biến động, rồi kiểm tra cách học residual quanh giá gần nhất có giúp cải thiện điểm–chi phí hay không. Mọi tuyên bố tính mới và hiệu quả sẽ giới hạn theo kết quả thực nghiệm và độ bao phủ literature.”

## 13. Nguồn chính và giới hạn hồ sơ

Các URL paper/code cụ thể được ghi theo từng phương pháp trong methods.json/Excel, kèm bản lưu evidence. Các nguồn trọng yếu:

- TiDE: https://arxiv.org/abs/2304.08424 ; code google-research/tide.
- TSMixer: https://arxiv.org/abs/2303.06053 ; code google-research/tsmixer.
- iTransformer: https://arxiv.org/abs/2310.06625 ; code thuml/iTransformer.
- TimeMixer: https://arxiv.org/abs/2405.14616 ; code kwuking/TimeMixer; venue ICLR 2024 xác nhận trong repo.
- TimeXer: https://arxiv.org/abs/2402.19072 ; code thuml/TimeXer.
- Chronos-2: https://arxiv.org/abs/2510.15821 ; code amazon-science/chronos-forecasting.
- Moirai2: https://arxiv.org/abs/2511.11698v3 ; code SalesforceAIResearch/uni2ts; Section 6 là bằng chứng bỏ covariates.
- TabPFN-TS: https://arxiv.org/abs/2501.02945v4 ; code PriorLabs/tabpfn-time-series.
- TimesFM3: https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/ ; weights https://huggingface.co/google/timesfm-3.0-pytorch .
- TiRex2: https://arxiv.org/abs/2607.01204 ; code NX-AI/tirex-2.

**Chưa hoàn tất:** benchmark/cài đặt 10 model, systematic domain literature search và tái lập mọi bảng paper. Không có kết quả thực nghiệm mới của 10 model trong hồ sơ này. Đây là hồ sơ related work + gap ứng viên + thiết kế triển khai, không phải bằng chứng nhóm đã vượt SOTA.