import os
import re

import fitz
from pypdf import PdfReader


def format_size(size_bytes):
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_idx = 0
    while size >= 1024 and unit_idx < len(units) - 1:
        size /= 1024
        unit_idx += 1
    if unit_idx == 0:
        return f"{int(size)} {units[unit_idx]}"
    return f"{size:.1f} {units[unit_idx]}"


def count_pdf_pages(file_path):
    try:
        reader = PdfReader(file_path)
        return len(reader.pages)
    except Exception:
        return None


def count_txt_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_obj:
            return sum(1 for _ in file_obj)
    except Exception:
        return None


def build_file_measure_lines(file_paths):
    lines = []
    for index, file_path in enumerate(sorted(file_paths), 1):
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            page_count = count_pdf_pages(file_path)
            if page_count is not None:
                lines.append(f"{index}. {filename}：{page_count}页")
                continue
        elif ext == ".txt":
            line_count = count_txt_lines(file_path)
            if line_count is not None:
                lines.append(f"{index}. {filename}：{line_count}行")
                continue

        lines.append(f"{index}. {filename}：")
    return lines


def _sample_page_indexes(page_count):
    if page_count <= 0:
        return []
    return sorted({min(page_count - 1, max(0, round((page_count - 1) * ratio))) for ratio in (0.10, 0.40, 0.70)})


def _extract_sampled_pdf_text(file_path):
    try:
        with fitz.open(file_path) as doc:
            if len(doc) == 0:
                return ""

            sampled_text = []
            for page_index in _sample_page_indexes(len(doc)):
                sampled_text.append(doc[page_index].get_text("text"))
            return "\n".join(sampled_text)
    except Exception:
        return ""


def detect_pdf_text_status(file_path):
    text = _extract_sampled_pdf_text(file_path)
    if not text:
        return "纯图片版"

    english_count = len(re.findall(r"[A-Za-z]", text))
    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    effective_count = english_count + chinese_count

    # Product copy should stay conservative: only PDFs with enough extractable
    # text are labeled as searchable/copyable, otherwise they fall back to image-only.
    if effective_count < 100:
        return "纯图片版"
    return "可复制可搜索"


def is_pdf_predominantly_english(file_path):
    text = _extract_sampled_pdf_text(file_path)
    if not text:
        return False

    english_count = len(re.findall(r"[A-Za-z]", text))
    chinese_count = len(re.findall(r"[\u4e00-\u9fff]", text))
    effective_count = english_count + chinese_count

    # The label should only appear for clearly English books, so low-text PDFs
    # or bilingual pages fail closed instead of being guessed as English originals.
    if effective_count < 100:
        return False
    return english_count / effective_count >= 0.85
