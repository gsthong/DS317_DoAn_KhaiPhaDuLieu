"""Export the source-audited review to XLSX and DOCX without model result fabrication."""

import importlib.util
import json
from pathlib import Path
import sys

from docx import Document
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "reports" / "sota_price_2023_2026"


def add_sheet(workbook, name, fields, methods):
    sheet = workbook.create_sheet(name)
    sheet.append([title for _, title in fields])
    for method in methods:
        sheet.append([method.get(key, "") for key, _ in fields])
    sheet.freeze_panes = "C2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    sheet.row_dimensions[1].height = 36
    for index, (key, _) in enumerate(fields, 1):
        sheet.column_dimensions[get_column_letter(index)].width = 10 if key in ("id", "year", "priority") else 48
    for row in sheet.iter_rows(min_row=2):
        sheet.row_dimensions[row[0].row].height = 145
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if isinstance(cell.value, str) and cell.value.startswith("https://"):
                cell.hyperlink = cell.value
                cell.font = Font(color="0563C1", underline="single")
    sheet.sheet_view.zoomScale = 75
    return sheet


def main():
    methods = json.loads((OUT / "methods.json").read_text(encoding="utf-8"))
    assert len(methods) == 10 and len({m["id"] for m in methods}) == 10
    assert all(2023 <= m["year"] <= 2026 and m["run_status"] == "NOT_RUN" for m in methods)
    workbook = Workbook()
    workbook.remove(workbook.active)
    add_sheet(workbook, "01_Tong_quan", [(k, t) for k, t in [
        ("id", "ID"), ("name", "Phương pháp"), ("year", "Năm"), ("publication", "Trạng thái xuất bản"),
        ("title", "Tên đầy đủ"), ("authors", "Tác giả"), ("paper", "Paper / release"), ("code", "Official code"),
        ("original_task", "Task gốc và mức liên quan"), ("mechanism", "Kiến trúc"), ("training", "Chế độ học")]], methods)
    add_sheet(workbook, "02_Ma_tran_nang_luc", [(k, t) for k, t in [
        ("id", "ID"), ("name", "Phương pháp"), ("past_covariates", "Ngoại sinh quá khứ"),
        ("future_covariates", "Ngoại sinh tương lai biết trước"), ("static", "Static metadata"),
        ("cross_variate", "Cross-variate"), ("probabilistic", "Uncertainty"), ("missing", "Missingness"),
        ("license", "Code / weights license")]], methods)
    add_sheet(workbook, "03_Ket_qua_CONG_BO", [(k, t) for k, t in [
        ("id", "ID"), ("name", "Phương pháp"), ("original_task", "Dataset / target gốc"),
        ("published_evidence", "KẾT QUẢ TÁC GIẢ – KHÔNG PHẢI ĐIỂM NHÓM"), ("paper", "Nguồn"),
        ("limitation", "Giới hạn diễn giải")]], methods)
    add_sheet(workbook, "04_Cai_dat_va_chay", [(k, t) for k, t in [
        ("id", "ID"), ("name", "Phương pháp"), ("priority", "Ưu tiên"), ("run_status", "Chạy dữ liệu nhóm"),
        ("implementation", "Môi trường / implementation"), ("adaptation", "Adapter cần làm"),
        ("license", "Rào cản giấy phép"), ("code", "Nguồn code")]], methods)
    add_sheet(workbook, "05_Uu_nhuoc_va_gap", [(k, t) for k, t in [
        ("id", "ID"), ("name", "Phương pháp"), ("strength", "Điểm mạnh"), ("limitation", "Hạn chế có bằng chứng"),
        ("adaptation", "Nhóm cần làm gì"), ("paper", "Nguồn")]], methods)
    notes = [
        {"id": "N01", "topic": "Phạm vi", "detail": "Chốt 06/11/2026. 10 phương pháp liên quan kỹ thuật, KHÔNG phải 10 paper trực tiếp SKU electronics price."},
        {"id": "N02", "topic": "Ký hiệu", "detail": "✓ có nguồn; — không hỗ trợ trong bản nêu; △ phụ thuộc bản/adapter; ? chưa xác minh. Không biến ? thành không có."},
        {"id": "N03", "topic": "Trạng thái", "detail": "Mọi model NOT_RUN trên dữ liệu nhóm. Paper/source audit đã thực hiện, cài và full benchmark chưa thực hiện."},
        {"id": "N04", "topic": "Gap", "detail": "Ứng viên: external validity, short/sparse observed transaction price, persistence/change regimes, availability-aware covariates, accuracy-cost. Chưa khẳng định novelty toàn literature."},
        {"id": "N05", "topic": "Đề xuất", "detail": "Single-target log price-ratio quanh last-price + recency/missingness + optional validation blending. Ablation raw/log/log-ratio, with/without features, with/without blend."},
        {"id": "N06", "topic": "Hai track", "detail": "A target-only chung thông tin; B valid covariates theo hỗ trợ, Moirai2 N/A. Không gọi ưu thế do nhiều feature là ưu thế kiến trúc thuần."},
        {"id": "N07", "topic": "Baseline", "detail": "Last-price, rolling price, Ridge, LightGBM ngoài bộ 10; baseline có thể cũ hơn 2023 và vẫn cần thiết."},
        {"id": "N08", "topic": "Bằng chứng", "detail": "Xem RELATED_WORK_VA_GAP.md và evidence/manifest.json. Không so số ở benchmarks khác nhau như cùng dataset."},
        {"id": "N09", "topic": "Máy hiện tại", "detail": "Windows, Python3.11.2, torch2.2.0+cpu, không CUDA. Không hứa latency/VRAM khi chưa pilot."},
    ]
    add_sheet(workbook, "06_Gap_va_protocol", [("id", "ID"), ("topic", "Hạng mục"), ("detail", "Nội dung")], notes)
    xlsx = OUT / "SoSanh_10_PhuongPhap_2023_2026.xlsx"
    workbook.save(xlsx)

    # Reuse the renderer already used in this repository, not a new document framework.
    spec = importlib.util.spec_from_file_location("proposal_renderer", ROOT / "src" / "build_price_proposal_doc.py")
    renderer = importlib.util.module_from_spec(spec)
    previous_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(renderer)
    finally:
        sys.dont_write_bytecode = previous_bytecode
    renderer.SOURCE = OUT / "RELATED_WORK_VA_GAP.md"
    renderer.OUTPUT = OUT / "RelatedWork_Va_Gap_2023_2026.docx"
    renderer.build_document()
    doc = Document(renderer.OUTPUT)
    doc.core_properties.title = "Related work 2023–2026 và gap dự báo giá SKU–tuần"
    doc.core_properties.subject = "Source-audited literature review; NOT a completed model benchmark"
    doc.save(renderer.OUTPUT)
    reopened = load_workbook(xlsx, read_only=True)
    assert len(reopened.sheetnames) == 6
    for sheet in list(reopened.worksheets)[:5]:
        assert sheet.max_row == 11
    assert reopened["04_Cai_dat_va_chay"]["D2"].value == "NOT_RUN"
    reopened.close()
    print("Verified Excel: 6 sheets, 10 methods, explicit NOT_RUN status")
    print("Verified Word:", len(Document(renderer.OUTPUT).paragraphs), "paragraphs")
    print(xlsx)
    print(renderer.OUTPUT)


if __name__ == "__main__":
    main()