import os

from src.domain.book_parser import is_obviously_english_named_book, parse_book_filename
from src.domain.file_metadata import (
    build_file_measure_lines,
    detect_pdf_text_status,
    format_size,
    is_pdf_predominantly_english,
)


FORMAT_ORDER = [".pdf", ".txt", ".docx", ".epub", ".mobi", ".azw3"]


def _get_format_labels(file_paths):
    seen_exts = {os.path.splitext(path)[1].lower() for path in file_paths}
    labels = [ext.strip(".").upper() for ext in FORMAT_ORDER if ext in seen_exts]
    return labels


def _get_delivery_count(file_paths, format_labels):
    if len(format_labels) <= 1:
        return len(file_paths)
    base_names = {os.path.splitext(os.path.basename(path))[0] for path in file_paths}
    return len(base_names)


def _should_mark_as_english_original(source_name, target_files):
    if not is_obviously_english_named_book(source_name):
        return False

    pdf_files = [path for path in target_files if os.path.splitext(path)[1].lower() == ".pdf"]
    if not pdf_files:
        return False
    return is_pdf_predominantly_english(pdf_files[0])


def _get_pdf_text_status(target_files):
    pdf_files = [path for path in target_files if os.path.splitext(path)[1].lower() == ".pdf"]
    if not pdf_files:
        return ""
    # Text status is based on the delivered PDF, including PDFs created during conversion.
    return detect_pdf_text_status(pdf_files[0])


def build_product_template(source_name, target_format, target_files):
    parsed = parse_book_filename(source_name)
    format_labels = _get_format_labels(target_files) or [target_format.upper()]
    source_ext = os.path.splitext(source_name)[1].lower()
    source_format = source_ext.strip(".").upper() if source_ext else ""
    # Multi-format products should expose the source format in the title/body,
    # because buyers often care that the bundle originated from EPUB instead of PDF-only.
    if len(format_labels) > 1 and source_format and source_format not in format_labels:
        format_labels.append(source_format)
    format_label = "/".join(format_labels)
    delivery_count = _get_delivery_count(target_files, format_labels)
    # A single delivery format is treated as multiple "volumes".
    # Multiple delivery formats for the same title are presented as one "set".
    delivery_unit = "册" if len(format_labels) == 1 else "套"
    total_size = sum(os.path.getsize(path) for path in target_files if os.path.exists(path))
    author_text = ", ".join(parsed["authors"])
    title_text = parsed["title"]
    measure_lines = build_file_measure_lines(target_files)
    is_english_original = _should_mark_as_english_original(source_name, target_files)
    pdf_text_status = _get_pdf_text_status(target_files)

    header_parts = [title_text]
    if author_text:
        header_parts.append(author_text)
    if is_english_original:
        header_parts.append("英文原版")
    header_parts.append(f"{format_label}格式共（{delivery_count}）{delivery_unit}")
    header_line = " ".join(part for part in header_parts if part)

    lines = [
        header_line,
        "",
        "1. 基本信息",
        "",
        f"资料名称： 《{title_text}》",
        "",
        f"作者： （{author_text}）" if author_text else "作者： （）",
        "",
        "资料语言： 英文原版" if is_english_original else "资料语言： ",
        "",
        f"文本状态： {pdf_text_status}" if pdf_text_status else "文本状态： ",
        "",
        f"文件格式： 高清 包含 {format_label} 电子版（非实体纸质书）",
        "",
        f"总文件大小： 约{format_size(total_size)}",
        "",
        "文件页数：",
        *measure_lines,
        "",
        "2. 发货方式",
        "度盘链接发送。",
        "",
        "3. 资料说明",
        "",
        "",
        "4. 购前必读（重要）",
        "虚拟商品，售出不退，看好再拍。",
        "有问题私聊，喜欢直接拍。",
    ]
    return "\n".join(lines)
