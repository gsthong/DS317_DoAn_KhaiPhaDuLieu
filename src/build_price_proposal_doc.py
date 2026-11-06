"""Render the preliminary single-task price proposal to Word, without changing old reports."""

from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "reports" / "ThuyetMinhSoBo_Nhom5_DuBaoGia_SKU_Tuan.md"
OUTPUT = SOURCE.with_suffix(".docx")


def add_inline(paragraph, text):
    """Support the bold emphasis used in the source while keeping Vietnamese intact."""
    for index, part in enumerate(re.split(r"\*\*(.*?)\*\*", text)):
        paragraph.add_run(part).bold = bool(index % 2)


def shade(cell, fill):
    properties = cell._tc.get_or_add_tcPr()
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), fill)
    properties.append(element)


def build_document():
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin, section.right_margin = Cm(2.3), Cm(1.8)
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    for name in ("Title", "Heading 1", "Heading 2", "Heading 3"):
        style = document.styles[name]
        style.font.name = "Times New Roman"
        style.font.color.rgb = RGBColor.from_string("17365D")
    document.styles["Heading 1"].font.size = Pt(15)
    document.styles["Heading 2"].font.size = Pt(13)
    document.styles["Heading 3"].font.size = Pt(12)

    header = section.header.paragraphs[0]
    header.text = "DS317.R11 – NHÓM 5 | THUYẾT MINH SƠ BỘ"
    header.style = document.styles["Caption"]
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run("Dự báo giá SKU–tuần | Trang ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("| "):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                row = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in row):
                    rows.append(row)
                index += 1
            if any(len(row) != len(rows[0]) for row in rows):
                raise ValueError("Inconsistent table column count")
            table = document.add_table(rows=1, cols=len(rows[0]))
            table.style = "Table Grid"
            for row_index, values in enumerate(rows):
                cells = table.rows[0].cells if row_index == 0 else table.add_row().cells
                for cell, text in zip(cells, values):
                    paragraph = cell.paragraphs[0]
                    add_inline(paragraph, text)
                    paragraph.paragraph_format.space_after = Pt(4)
                    for run in paragraph.runs:
                        run.font.size = Pt(10.5)
                        if row_index == 0:
                            run.bold = True
                    if row_index == 0:
                        shade(cell, "DFEAF5")
                if row_index == 0:
                    repeat = OxmlElement("w:tblHeader")
                    table.rows[0]._tr.get_or_add_trPr().append(repeat)
            document.add_paragraph()
            continue
        if line.startswith("# "):
            paragraph = document.add_paragraph(style="Title")
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_inline(paragraph, line[2:])
        elif line.startswith("## "):
            text = line[3:]
            paragraph = document.add_paragraph(text, style="Heading 1")
            if text.startswith("Phần A."):
                paragraph.paragraph_format.page_break_before = True
        elif line.startswith("### "):
            document.add_paragraph(line[4:], style="Heading 2")
        elif line.startswith("- "):
            add_inline(document.add_paragraph(style="List Bullet"), line[2:])
        elif re.match(r"^\d+\. ", line):
            add_inline(document.add_paragraph(style="List Number"), re.sub(r"^\d+\. ", "", line))
        else:
            add_inline(document.add_paragraph(), line)
        index += 1

    document.core_properties.title = "Dự báo giá bán thực tế theo SKU–tuần trong bán lẻ điện máy"
    document.core_properties.subject = "Thuyết minh sơ bộ – một nhiệm vụ dự báo giá"
    document.core_properties.author = "Nhóm 5 – DS317.R11"
    document.core_properties.comments = "Đề xuất; không phải báo cáo kết quả thực nghiệm đã hoàn tất."
    document.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    output = build_document()
    # Reopen the generated package to verify that Word content was actually written.
    checked = Document(output)
    text = "\n".join(paragraph.text for paragraph in checked.paragraphs)
    for number in range(1, 14):
        assert f"Mục {number}." in text, f"Missing section {number}"
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    expected_tables = sum(
        line.startswith("| ") and (index == 0 or not source_lines[index - 1].startswith("| "))
        for index, line in enumerate(source_lines)
    )
    assert len(checked.tables) == expected_tables, "A source table was lost during rendering"
    assert len(checked.inline_shapes) == 0
    print(f"Created and reopened: {output}")
    print(f"Paragraphs: {len(checked.paragraphs)}; tables: {len(checked.tables)}")