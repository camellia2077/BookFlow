from pathlib import Path

import fitz
from pypdf import PdfWriter

from src.domain.product_formatter import build_product_template


def _write_pdf(path: Path, page_count: int = 1):
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as file_obj:
        writer.write(file_obj)


def _write_text_pdf(path: Path, pages: list[str]):
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


def test_build_product_template_for_single_delivery_format_uses_ce():
    files = [
        r"C:\books\万历野获编 - 上册.pdf",
        r"C:\books\万历野获编 - 下册.pdf",
        r"C:\books\万历野获编 - 中册.pdf",
        r"C:\books\万历野获编 - 附录.pdf",
    ]

    template = build_product_template(r"C:\books\[明] 沈德符 - 万历野获编.epub", "pdf", files)

    assert template.splitlines()[0] == "万历野获编 沈德符 PDF格式共（4）册"
    assert "文件格式： 高清 包含 PDF 电子版（非实体纸质书）" in template
    assert "文本状态： 纯图片版" in template


def test_build_product_template_for_multi_delivery_format_includes_source_format(tmp_path: Path):
    source = tmp_path / "[美] 乔纳森·巴尔科姆 - 鱼什么都知道.epub"
    source.write_text("", encoding="utf-8")

    pdf_path = tmp_path / "[美] 乔纳森·巴尔科姆 - 鱼什么都知道.pdf"
    _write_pdf(pdf_path)

    txt_path = tmp_path / "[美] 乔纳森·巴尔科姆 - 鱼什么都知道.txt"
    txt_path.write_text("a\n", encoding="utf-8")

    docx_path = tmp_path / "[美] 乔纳森·巴尔科姆 - 鱼什么都知道.docx"
    docx_path.write_bytes(b"docx")

    template = build_product_template(str(source), "pdf", [str(pdf_path), str(txt_path), str(docx_path)])

    assert template.splitlines()[0] == "鱼什么都知道 乔纳森·巴尔科姆 PDF/TXT/DOCX/EPUB格式共（1）套"
    assert "文件格式： 高清 包含 PDF/TXT/DOCX/EPUB 电子版（非实体纸质书）" in template
    assert "原始格式：" not in template
    assert "文本状态： 纯图片版" in template


def test_build_product_template_marks_english_original_when_name_and_pdf_text_are_english(tmp_path: Path):
    source = tmp_path / "Morgan Hale - Northern Fleet Records, 2001-2022.epub"
    source.write_text("", encoding="utf-8")

    pdf_path = tmp_path / "Morgan Hale - Northern Fleet Records, 2001-2022.pdf"
    _write_text_pdf(
        pdf_path,
        [
            "Cover page",
            "Naval reference work and fleet listing.",
            "The fleet tables describe ship classes and operations in detail.",
            "These chapters examine command structure, logistics, and strategy.",
            "Appendix and notes for further study.",
        ],
    )

    template = build_product_template(str(source), "pdf", [str(pdf_path)])

    assert template.splitlines()[0] == "Northern Fleet Records, 2001-2022 Morgan Hale 英文原版 PDF格式共（1）册"
    assert "资料语言： 英文原版" in template
    assert "文本状态： 可复制可搜索" in template


def test_build_product_template_does_not_mark_english_without_pdf_text_confirmation(tmp_path: Path):
    source = tmp_path / "Morgan Hale - Northern Fleet Records, 2001-2022.epub"
    source.write_text("", encoding="utf-8")

    pdf_path = tmp_path / "Morgan Hale - Northern Fleet Records, 2001-2022.pdf"
    _write_pdf(pdf_path)

    template = build_product_template(str(source), "pdf", [str(pdf_path)])

    assert "英文原版" not in template.splitlines()[0]
    assert "资料语言： 英文原版" not in template
    assert "文本状态： 纯图片版" in template
