from pathlib import Path

import fitz
import pytest

from src.infrastructure.pdf_preview_generator import find_toc_page_index, generate_pdf_preview_images
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


def _create_realistic_chinese_book_pdf(path: Path):
    cjk_font = _get_available_cjk_font()
    if cjk_font is None:
        pytest.skip("No Windows CJK font available for Chinese realistic PDF test.")

    doc = fitz.open()
    pages = [
        "北境行旅笔记",
        "版权页\n再版说明",
        "北境行旅笔记\n原书序言(摘要)\n再版说明\n第一章 山谷里的清晨\n第二章 初次远行\n第三章 风雪中的营地\n第四章 越过旧边界",
        "前言\n这是一段关于旅程与观察的记录。",
        "插图说明\n照片与地图索引。",
        "第一章 山谷里的清晨\n最早的记忆总和薄雾、钟声以及清冷的河岸连在一起。",
        "第二章 初次远行\n第一次离开故乡时，路标和山势都显得陌生而新鲜。",
        "第三章 风雪中的营地\n恶劣天气迫使每个人重新学习节奏与协作。",
        "第四章 越过旧边界\n视野越过熟悉地带之后，判断开始变得更重要。",
        "第五章 北地长桥\n新的地形总会带来新的选择。",
    ]

    for text in pages:
        page = doc.new_page()
        _insert_text(page, text, cjk_font)

    doc.save(path)
    doc.close()


def _create_realistic_english_book_pdf(path: Path):
    doc = fitz.open()
    pages = [
        "Notes from the Northern Road",
        "Copyright and Edition Notes",
        "Contents\nChapter 1 Dawn in the Valley\nChapter 2 First Departure\nChapter 3 Camp in the Snow\nChapter 4 Beyond the Old Border",
        "Preface\nThese notes describe a long journey across changing terrain.",
        "Illustrations",
        "Chapter 1 Dawn in the Valley\nThe first mornings of travel set the tone for the whole route.",
        "Chapter 2 First Departure\nLeaving home made every road sign feel newly important.",
        "Chapter 3 Camp in the Snow\nHarsh weather forced the group to invent better routines.",
        "Chapter 4 Beyond the Old Border\nThe farther we moved, the more careful each decision became.",
        "Chapter 5 The Northern Bridge\nA new crossing changed the scale of the journey.",
    ]

    for text in pages:
        page = doc.new_page()
        _insert_text(page, text)

    doc.save(path)
    doc.close()


def _create_image_only_pdf(path: Path):
    doc = fitz.open()
    for label in ["Cover", "Image Page 1", "Image Page 2", "Image Page 3", "Image Page 4", "Image Page 5"]:
        page = doc.new_page()
        rect = fitz.Rect(72, 72, 400, 300)
        page.draw_rect(rect, color=(0, 0, 0), fill=(0.95, 0.95, 0.95))
        page.draw_line(rect.tl, rect.br, color=(0, 0, 0))
        page.draw_line(rect.tr, rect.bl, color=(0, 0, 0))
        # This keeps the PDF visual, but without a usable text layer for TOC detection.
        page.insert_text((90, 340), label, render_mode=3)

    doc.save(path)
    doc.close()


def test_blackbox_chinese_book_detects_toc_and_generates_ordered_images(tmp_path: Path):
    pdf_path = tmp_path / "northern_notes_zh.pdf"
    _create_realistic_chinese_book_pdf(pdf_path)

    assert find_toc_page_index(str(pdf_path)) == 2

    generated = generate_pdf_preview_images(str(pdf_path), str(tmp_path))
    names = [Path(path).name for path in generated]

    assert names[0].startswith("01_封面_p001_")
    assert names[1].startswith("02_目录_p003_")
    assert names[2].startswith("03_内页_p006_")
    assert names[3].startswith("04_内页_p007_")


def test_blackbox_english_book_detects_contents_and_generates_ordered_images(tmp_path: Path):
    pdf_path = tmp_path / "northern_notes_en.pdf"
    _create_realistic_english_book_pdf(pdf_path)

    assert find_toc_page_index(str(pdf_path)) == 2

    generated = generate_pdf_preview_images(str(pdf_path), str(tmp_path))
    names = [Path(path).name for path in generated]

    assert len(generated) == 4
    assert names[0].startswith("01_封面_p001_")
    assert names[1].startswith("02_目录_p003_")
    assert names[2].startswith("03_内页_p006_")
    assert names[3].startswith("04_内页_p007_")


def test_blackbox_image_only_pdf_skips_toc_image(tmp_path: Path):
    pdf_path = tmp_path / "image_only.pdf"
    _create_image_only_pdf(pdf_path)

    generated = generate_pdf_preview_images(str(pdf_path), str(tmp_path))
    names = [Path(path).name for path in generated]
    image_dir = tmp_path / PRODUCT_IMAGE_DIRNAME

    assert image_dir.exists()
    assert len(generated) == 3
    assert names[0].startswith("01_封面_p001_")
    assert names[1].startswith("03_内页_p005_")
    assert names[2].startswith("04_内页_p006_")
    assert not any("目录" in name for name in names)
