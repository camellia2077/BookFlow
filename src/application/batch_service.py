import os
import shutil
import sys

from src.application.product_service import write_product_description, write_product_summary
from src.infrastructure.calibre_converter import check_environment, run_conversion_task, validate_content
from src.infrastructure.file_ops import (
    collect_target_files,
    copy_directory_filtered,
    generate_directory_readme,
    write_info_summary,
)
from src.infrastructure.zip_archiver import compress_directory
from src.presentation.console import (
    display_archive_error,
    display_archive_success,
    display_batch_summary,
    display_error,
    display_final,
    display_progress,
    display_scan_result,
    display_success,
)

_ENGINE_PATH = None


def _get_engine():
    global _ENGINE_PATH
    if _ENGINE_PATH is None:
        _ENGINE_PATH = check_environment()
    return _ENGINE_PATH


def convert_single_file(input_path, target_format, scan_only=False):
    file_name = os.path.basename(input_path)
    generated_files = []

    found_risks = validate_content(input_path)
    if scan_only:
        display_scan_result(file_name, found_risks)
        return False, generated_files
    if found_risks:
        sys.stdout.write(f"\n[安全拦截]: 检测到风险词 {found_risks}，已终止文件 '{file_name}'。\n")
        return False, generated_files

    try:
        engine_path = _get_engine()
    except Exception as exc:
        sys.stdout.write(f"环境错误: {exc}\n")
        return False, generated_files

    base_name, input_ext = os.path.splitext(input_path)
    input_ext = input_ext.lower().strip(".")
    formats = ["pdf", "txt", "docx"] if (input_ext in ["epub", "mobi", "azw3"] and target_format == "pdf") else [target_format]

    total = len(formats)
    has_success = False
    for index, current_format in enumerate(formats, 1):
        output_path = f"{base_name}.{current_format}"
        display_progress(index, total, current_format, file_name)

        if run_conversion_task(engine_path, input_path, output_path, current_format):
            display_success(current_format, output_path)
            has_success = True
            generated_files.append(output_path)
        else:
            display_error(current_format)

    display_final(file_name)
    return has_success, generated_files


def process_directory_batch(dir_path, target_format, scan_only=False):
    source_exts = {".epub", ".mobi", ".azw3"}
    target_output_ext = f".{target_format.lower()}"
    readme_whitelist = source_exts | {".pdf", ".txt", ".docx"}

    compressed_count = 0
    skipped_count = 0
    error_count = 0
    all_info_texts = []
    product_texts = []

    abs_dir_path = os.path.abspath(dir_path)
    archive_out_dir = f"{abs_dir_path}_输出归档"
    if not scan_only:
        os.makedirs(archive_out_dir, exist_ok=True)

    for root, dirs, files in os.walk(dir_path, topdown=False):
        if root.startswith(archive_out_dir):
            continue

        source_files = [f for f in files if os.path.splitext(f)[1].lower() in source_exts]
        has_target_output = any(os.path.splitext(f)[1].lower() == target_output_ext for f in files)

        if not source_files and not has_target_output:
            if not dirs:
                skipped_count += 1
            continue

        if not source_files and has_target_output:
            if not scan_only:
                readme_content = generate_directory_readme(root, target_exts=readme_whitelist)
                if readme_content:
                    all_info_texts.append(f"📁 【纯目标格式目录】: {root}\n{readme_content}")
                product_files = collect_target_files(root, target_format)
                if product_files:
                    product_description_path = write_product_description(root, product_files[0], target_format, product_files)
                    if product_description_path:
                        with open(product_description_path, "r", encoding="utf-8") as file_obj:
                            product_texts.append(f"📦 {root}\n{file_obj.read()}")

                    target_copy_dir = os.path.join(archive_out_dir, os.path.basename(root))
                    success, result_msg = copy_directory_filtered(root, target_copy_dir)
                    if success:
                        display_archive_success(result_msg)
                        compressed_count += 1
                    else:
                        display_archive_error(root, result_msg)
                        error_count += 1
            else:
                skipped_count += 1
            continue

        sys.stdout.write(f"\n" + "=" * 40 + f"\n[扫描目录]: {root}\n")
        dir_has_converted = False
        dir_generated_files = []

        for file_name in source_files:
            full_path = os.path.join(root, file_name)
            success, generated_files = convert_single_file(full_path, target_format, scan_only)
            if success:
                dir_has_converted = True
            dir_generated_files.extend(generated_files)

        if dir_has_converted and not scan_only:
            readme_content = generate_directory_readme(root, target_exts=readme_whitelist)
            if readme_content:
                all_info_texts.append(f"📁 【归档目录】: {root}\n{readme_content}")

            product_files = collect_target_files(root, target_format)
            if product_files:
                product_description_path = write_product_description(root, product_files[0], target_format, product_files)
                if product_description_path:
                    with open(product_description_path, "r", encoding="utf-8") as file_obj:
                        product_texts.append(f"📦 {root}\n{file_obj.read()}")

            success, result_msg = compress_directory(root)
            if success:
                try:
                    zip_filename = os.path.basename(result_msg)
                    final_zip_path = os.path.join(archive_out_dir, zip_filename)

                    if os.path.exists(final_zip_path):
                        os.remove(final_zip_path)
                    shutil.move(result_msg, final_zip_path)

                    display_archive_success(final_zip_path)
                    compressed_count += 1
                except Exception as exc:
                    sys.stdout.write(f"  [归档迁移异常，强制滞留于原地]: {exc}\n")
                    compressed_count += 1

                for generated_path in dir_generated_files:
                    try:
                        if os.path.exists(generated_path):
                            os.remove(generated_path)
                    except Exception as exc:
                        sys.stdout.write(f"  [清理警告]: 无法删除残留文件 {generated_path} - {exc}\n")
            else:
                display_archive_error(root, result_msg)
                error_count += 1
        else:
            if not scan_only:
                readme_content = generate_directory_readme(root, target_exts=readme_whitelist)
                if readme_content:
                    all_info_texts.append(f"📁 【未发生转换目录】: {root}\n{readme_content}")
                product_files = collect_target_files(root, target_format)
                if product_files:
                    product_description_path = write_product_description(root, product_files[0], target_format, product_files)
                    if product_description_path:
                        with open(product_description_path, "r", encoding="utf-8") as file_obj:
                            product_texts.append(f"📦 {root}\n{file_obj.read()}")
            skipped_count += 1

    return compressed_count, skipped_count, error_count, all_info_texts, product_texts


def run_batch_workflow(input_path, user_format, scan_only=False):
    if os.path.isfile(input_path):
        success, generated_files = convert_single_file(input_path, user_format, scan_only)
        if success and not scan_only:
            target_files = [path for path in generated_files if os.path.splitext(path)[1].lower() == f".{user_format.lower()}"]
            if target_files:
                try:
                    output_path = write_product_description(os.path.dirname(input_path), input_path, user_format, target_files)
                    sys.stdout.write(f"\n[商品介绍]: 已生成 -> {os.path.join(os.path.dirname(input_path), '商品介绍.txt')}\n")
                except Exception as exc:
                    sys.stdout.write(f"\n❌ [商品介绍生成失败]: {exc}\n")
        return

    if os.path.isdir(input_path):
        c_count, s_count, e_count, all_info_texts, product_texts = process_directory_batch(input_path, user_format, scan_only)
        display_batch_summary(c_count, s_count, e_count)

        if all_info_texts and not scan_only:
            info_path = os.path.join(os.getcwd(), "output", "info.txt")
            write_info_summary(info_path, "📊 批量任务文件信息统计汇总", all_info_texts, "[信息汇总]")

        if product_texts and not scan_only:
            product_info_path = os.path.join(os.getcwd(), "output", "商品介绍汇总.txt")
            write_product_summary(product_info_path, product_texts)
