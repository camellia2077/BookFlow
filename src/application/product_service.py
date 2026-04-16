import os

from src.domain.product_formatter import build_product_template
from src.utils.timestamps import build_timestamped_filename


def write_product_description(output_dir, source_name, target_format, target_files):
    if not target_files:
        return ""

    description_text = build_product_template(source_name, target_format, target_files)
    output_path = os.path.join(output_dir, build_timestamped_filename("商品介绍", "txt"))
    with open(output_path, "w", encoding="utf-8") as file_obj:
        file_obj.write(description_text)
    return output_path


def write_product_summary(output_dir, product_texts):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, build_timestamped_filename("商品介绍汇总", "txt"))
    try:
        with open(output_path, "w", encoding="utf-8") as file_obj:
            file_obj.write("=" * 50 + "\n")
            file_obj.write("📦 批量商品介绍汇总\n")
            file_obj.write("=" * 50 + "\n\n")
            separator = "\n\n" + ("-" * 50) + "\n\n"
            file_obj.write(separator.join(product_texts))
        print(f"\n[商品介绍汇总]: 已生成 -> {output_path}")
    except Exception as exc:
        print(f"\n❌ [商品介绍汇总失败]: 无法写入文件 {output_path} - {exc}")
