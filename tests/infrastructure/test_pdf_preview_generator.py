from pathlib import Path

import fitz
import pytest

from src.infrastructure.pdf_preview_generator import (
    find_toc_page_index,
    generate_pdf_preview_images,
    select_content_page_indexes,
)
from src.settings import PRODUCT_IMAGE_DIRNAME


WINDOWS_CJK_FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\msyh.ttf"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
)


def _get_available_cjk_font():
    for font_path in WINDOWS_CJK_FONT_CANDIDATES:
        if font_path.exists():
            return font_path
    return None


def _insert_text(page, text: str, font_path: Path | None = None):
    if font_path is None:
        page.insert_text((72, 72), text)
        return

    page.insert_font(fontname="cjkfont", fontfile=str(font_path))
    page.insert_text((72, 72), text, fontname="cjkfont")


def _create_sample_pdf(path: Path, *, use_chinese_text: bool = False):
    doc = fitz.open()
    cjk_font = _get_available_cjk_font() if use_chinese_text else None
    page = doc.new_page()
    _insert_text(page, "封面" if use_chinese_text else "Cover", cjk_font)
    page = doc.new_page()
    _insert_text(page, "版权页" if use_chinese_text else "Copyright", cjk_font)
    page = doc.new_page()
    _insert_text(
        page,
        "目录\n第一章 山谷里的清晨\n第二章 初次远行" if use_chinese_text else "Contents\nChapter 1 Dawn in the Valley\nChapter 2 First Departure",
        cjk_font,
    )
    for index in range(7):
        page = doc.new_page()
        _insert_text(page, f"正文第{index + 1}页" if use_chinese_text else f"Page {index + 1}", cjk_font)
    doc.save(path)
    doc.close()


def test_find_toc_page_index_returns_matching_page(tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    _create_sample_pdf(pdf_path)

    assert find_toc_page_index(str(pdf_path)) == 2


def test_find_toc_page_index_returns_matching_page_for_chinese_toc(tmp_path: Path):
    cjk_font = _get_available_cjk_font()
    if cjk_font is None:
        pytest.skip("No Windows CJK font available for Chinese PDF extraction test.")

    pdf_path = tmp_path / "sample_zh.pdf"
    _create_sample_pdf(pdf_path, use_chinese_text=True)

    assert find_toc_page_index(str(pdf_path)) == 2


def test_find_toc_page_index_accepts_dense_chapter_patterns_without_contents_keyword(tmp_path: Path):
    pdf_path = tmp_path / "chapter_only.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Cover")
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Chapter 1 Dawn in the Valley\nChapter 2 First Departure\nChapter 3 Camp in the Snow\nChapter 4 Beyond the Old Border",
    )
    page = doc.new_page()
    page.insert_text((72, 72), "Body")
    doc.save(pdf_path)
    doc.close()

    assert find_toc_page_index(str(pdf_path)) == 1


def test_find_toc_page_index_accepts_dense_chinese_chapter_patterns(tmp_path: Path):
    cjk_font = _get_available_cjk_font()
    if cjk_font is None:
        pytest.skip("No Windows CJK font available for Chinese chapter pattern test.")

    pdf_path = tmp_path / "chapter_only_zh.pdf"
    doc = fitz.open()
    page = doc.new_page()
    _insert_text(page, "封面", cjk_font)
    page = doc.new_page()
    _insert_text(
        page,
        "第一章 山谷里的清晨\n第二章 初次远行\n第三章 风雪中的营地\n第四章 越过旧边界",
        cjk_font,
    )
    page = doc.new_page()
    _insert_text(page, "正文", cjk_font)
    doc.save(pdf_path)
    doc.close()

    assert find_toc_page_index(str(pdf_path)) == 1


def test_select_content_page_indexes_skips_cover_and_toc():
    indexes = select_content_page_indexes(10, exclude_indexes={0, 2}, preview_count=2)

    assert indexes == [5, 6]


def test_select_content_page_indexes_uses_percentage_targets_for_larger_books():
    indexes = select_content_page_indexes(100, exclude_indexes={0, 30, 64}, preview_count=2)

    assert indexes == [31, 65]


def test_generate_pdf_preview_images_creates_cover_content_and_toc_images(tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    _create_sample_pdf(pdf_path)

    generated = generate_pdf_preview_images(str(pdf_path), str(tmp_path))
    image_dir = tmp_path / PRODUCT_IMAGE_DIRNAME

    assert image_dir.exists()
    names = [Path(path).name for path in generated]
    assert len(names) == 4
    assert names[0].startswith("01_封面_p001_")
    assert names[1].startswith("02_目录_p003_")
    assert names[2].startswith("03_内页_p006_")
    assert names[3].startswith("04_内页_p007_")
    for path in generated:
        assert Path(path).exists()
