import fitz
from pathlib import Path

from pypdf import PdfWriter

from src.domain.file_metadata import (
    build_file_measure_lines,
    count_pdf_pages,
    count_txt_lines,
    detect_pdf_text_status,
    format_size,
)


def test_format_size_outputs_human_readable_units():
    assert format_size(512) == "512 B"
    assert format_size(1024) == "1.0 KB"


def test_count_txt_lines_counts_lines(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("a\nb\nc\n", encoding="utf-8")

    assert count_txt_lines(str(file_path)) == 3


def test_count_pdf_pages_reads_page_count(tmp_path: Path):
    file_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_blank_page(width=72, height=72)
    with open(file_path, "wb") as file_obj:
        writer.write(file_obj)

    assert count_pdf_pages(str(file_path)) == 2


def test_build_file_measure_lines_renders_pdf_and_txt(tmp_path: Path):
    pdf_path = tmp_path / "a.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as file_obj:
        writer.write(file_obj)

    txt_path = tmp_path / "b.txt"
    txt_path.write_text("1\n2\n", encoding="utf-8")

    assert build_file_measure_lines([str(pdf_path), str(txt_path)]) == [
        "1. a.pdf：1页",
        "2. b.txt：2行",
    ]


def test_detect_pdf_text_status_marks_text_pdf_as_searchable(tmp_path: Path):
    pdf_path = tmp_path / "text.pdf"
    doc = fitz.open()
    for text in [
        "This page contains enough English text to be searchable and copyable by the reader.",
        "Additional chapter notes and references are included for full text extraction coverage.",
        "A long appendix provides more searchable wording for the final sampled pages.",
    ]:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    doc.save(pdf_path)
    doc.close()

    assert detect_pdf_text_status(str(pdf_path)) == "可复制可搜索"


def test_detect_pdf_text_status_marks_blank_pdf_as_image_only(tmp_path: Path):
    pdf_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    for _ in range(3):
        writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as file_obj:
        writer.write(file_obj)

    assert detect_pdf_text_status(str(pdf_path)) == "纯图片版"
