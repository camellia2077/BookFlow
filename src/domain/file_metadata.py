import os

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

