import os

from src.domain.book_parser import parse_book_filename
from src.domain.file_metadata import build_file_measure_lines, format_size


def build_product_template(source_name, target_format, target_files):
    parsed = parse_book_filename(source_name)
    format_label = target_format.upper()
    book_count = len(target_files)
    total_size = sum(os.path.getsize(path) for path in target_files if os.path.exists(path))
    author_text = ", ".join(parsed["authors"])
    title_text = parsed["title"]
    measure_lines = build_file_measure_lines(target_files)

    header_parts = [title_text]
    if author_text:
        header_parts.append(author_text)
    header_parts.append(f"{format_label}格式共（{book_count}）册")
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
        f"文件格式： 高清 {format_label} 电子版（非实体纸质书）",
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

