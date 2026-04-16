import os
import shutil
import sys

from src.application.product_service import write_product_description, write_product_summary
from src.domain.book_parser import parse_book_filename
from src.infrastructure.calibre_converter import check_environment, run_conversion_task, validate_content
from src.infrastructure.file_ops import (
    clear_generated_artifacts,
    collect_delivery_files,
    collect_pdf_files,
    copy_directory_filtered,
    generate_directory_readme,
    write_info_summary,
)
from src.infrastructure.pdf_preview_generator import generate_pdf_preview_images
from src.infrastructure.zip_archiver import compress_directory
from src.presentation.console import (
    display_archive_error,
    display_archive_success,
    display_batch_summary,
    display_error,
    display_final,
    display_invalid_name,
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


def generate_product_images(output_dir, delivery_files):
    # Product screenshots are always based on an existing PDF, even when the
    # delivery set also includes TXT or DOCX. The first PDF acts as the visual source.
    pdf_files = [path for path in delivery_files if os.path.splitext(path)[1].lower() == ".pdf"]
    if not pdf_files:
        return []
    return generate_pdf_preview_images(pdf_files[0], output_dir)


def generate_product_images_from_existing_pdfs(input_path):
    summary = {
        "generated_count": 0,
        "pdf_found": False,
    }

    if os.path.isfile(input_path):
        if os.path.splitext(input_path)[1].lower() != ".pdf":
            return summary
        summary["pdf_found"] = True
        parsed_name = parse_book_filename(input_path)
        if not parsed_name["is_expected_format"]:
            display_invalid_name(os.path.basename(input_path))
            return summary
        clear_generated_artifacts(os.path.dirname(input_path))
        summary["generated_count"] = 1 if generate_pdf_preview_images(input_path, os.path.dirname(input_path)) else 0
        return summary

    for root, _, _ in os.walk(input_path):
        pdf_files = collect_pdf_files(root)
        if not pdf_files:
            continue
        summary["pdf_found"] = True

        # Image-only mode works on the original directory contents.
        # It never converts or archives files, and only needs one representative PDF.
        parsed_name = parse_book_filename(pdf_files[0])
        if not parsed_name["is_expected_format"]:
            display_invalid_name(os.path.basename(pdf_files[0]))
            continue

        clear_generated_artifacts(root)
        if generate_pdf_preview_images(pdf_files[0], root):
            summary["generated_count"] += 1
    return summary


def convert_single_file(input_path, target_format, scan_only=False):
    file_name = os.path.basename(input_path)
    generated_files = []
    parsed_name = parse_book_filename(input_path)

    # The automation pipeline is intentionally strict: if the filename does not
    # match the seller's naming convention, we stop early instead of guessing.
    if not parsed_name["is_expected_format"]:
        if not scan_only:
            display_invalid_name(file_name)
        return False, generated_files, True

    found_risks = validate_content(input_path)
    if scan_only:
        display_scan_result(file_name, found_risks)
        return False, generated_files, False
    if found_risks:
        sys.stdout.write(f"\n[安全拦截]: 检测到风险词 {found_risks}，已终止文件 '{file_name}'。\n")
        return False, generated_files, False

    try:
        engine_path = _get_engine()
    except Exception as exc:
        sys.stdout.write(f"环境错误: {exc}\n")
        return False, generated_files, False

    base_name, input_ext = os.path.splitext(input_path)
    input_ext = input_ext.lower().strip(".")
    # PDF is a special delivery mode for ebook sources:
    # besides the PDF itself, we also keep TXT and DOCX for resale convenience.
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
    return has_success, generated_files, False


def process_directory_batch(dir_path, target_format, scan_only=False, no_archive=False):
    source_exts = {".epub", ".mobi", ".azw3"}
    target_output_ext = f".{target_format.lower()}"
    readme_whitelist = source_exts | {".pdf", ".txt", ".docx"}

    compressed_count = 0
    skipped_count = 0
    error_count = 0
    invalid_name_count = 0
    invalid_name_files = []
    all_info_texts = []
    product_texts = []

    abs_dir_path = os.path.abspath(dir_path)
    archive_out_dir = f"{abs_dir_path}_输出归档"
    if not scan_only and not no_archive:
        # Archive output is rebuilt from scratch on every run.
        # The project data is small enough that we prefer a clean snapshot over
        # incremental updates, which keeps the exported folder deterministic.
        if os.path.exists(archive_out_dir):
            shutil.rmtree(archive_out_dir)
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

        # "Pure target format" means the directory already contains the delivery PDFs
        # and does not need conversion. We still generate metadata and product assets.
        if not source_files and has_target_output:
            if not scan_only:
                # Generated helper files are rebuilt on every run, so we wipe the
                # previous batch first to avoid accumulating timestamped duplicates.
                clear_generated_artifacts(root)
                readme_content = generate_directory_readme(root, target_exts=readme_whitelist)
                if readme_content:
                    all_info_texts.append(f"📁 【纯目标格式目录】: {root}\n{readme_content}")
                product_files = collect_delivery_files(root)
                if product_files:
                    parsed_name = parse_book_filename(product_files[0])
                    if not parsed_name["is_expected_format"]:
                        invalid_filename = os.path.basename(product_files[0])
                        display_invalid_name(invalid_filename)
                        invalid_name_count += 1
                        invalid_name_files.append(os.path.join(root, invalid_filename))
                    else:
                        product_description_path = write_product_description(root, product_files[0], target_format, product_files)
                        generate_product_images(root, product_files)
                        if product_description_path:
                            with open(product_description_path, "r", encoding="utf-8") as file_obj:
                                product_texts.append(f"📦 {root}\n{file_obj.read()}")

                        if no_archive:
                            # "No archive" is still a successful processing mode:
                            # metadata and screenshots are refreshed, but nothing is exported.
                            skipped_count += 1
                        else:
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
            success, generated_files, invalid_name = convert_single_file(full_path, target_format, scan_only)
            if invalid_name:
                invalid_name_count += 1
                invalid_name_files.append(full_path)
                continue
            if success:
                dir_has_converted = True
            dir_generated_files.extend(generated_files)

        # Once at least one source file converted successfully, the directory is treated
        # as a completed product folder: metadata is refreshed, screenshots are generated,
        # and optional archive/export steps run afterwards.
        if dir_has_converted and not scan_only:
            clear_generated_artifacts(root)
            readme_content = generate_directory_readme(root, target_exts=readme_whitelist)
            if readme_content:
                all_info_texts.append(f"📁 【归档目录】: {root}\n{readme_content}")

            product_files = collect_delivery_files(root)
            if product_files:
                source_name = os.path.join(root, source_files[0]) if source_files else product_files[0]
                product_description_path = write_product_description(root, source_name, target_format, product_files)
                generate_product_images(root, product_files)
                if product_description_path:
                    with open(product_description_path, "r", encoding="utf-8") as file_obj:
                        product_texts.append(f"📦 {root}\n{file_obj.read()}")

            if no_archive:
                # Conversion-only mode keeps the generated files in place for manual review.
                skipped_count += 1
            else:
                success, result_msg = compress_directory(root)
                if success:
                    try:
                        zip_filename = os.path.basename(result_msg)
                        final_zip_path = os.path.join(archive_out_dir, zip_filename)
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
                clear_generated_artifacts(root)
                readme_content = generate_directory_readme(root, target_exts=readme_whitelist)
                if readme_content:
                    all_info_texts.append(f"📁 【未发生转换目录】: {root}\n{readme_content}")
                product_files = collect_delivery_files(root)
                if product_files:
                    source_name = os.path.join(root, source_files[0]) if source_files else product_files[0]
                    product_description_path = write_product_description(root, source_name, target_format, product_files)
                    generate_product_images(root, product_files)
                    if product_description_path:
                        with open(product_description_path, "r", encoding="utf-8") as file_obj:
                            product_texts.append(f"📦 {root}\n{file_obj.read()}")
            skipped_count += 1

    return compressed_count, skipped_count, error_count, invalid_name_count, invalid_name_files, all_info_texts, product_texts


def run_batch_workflow(input_path, user_format, scan_only=False, no_archive=False):
    if os.path.isfile(input_path):
        success, generated_files, invalid_name = convert_single_file(input_path, user_format, scan_only)
        if invalid_name:
            return
        if success and not scan_only:
            delivery_files = [path for path in generated_files if os.path.splitext(path)[1].lower() in {".pdf", ".txt", ".docx"}]
            if delivery_files:
                try:
                    parent_dir = os.path.dirname(input_path)
                    clear_generated_artifacts(parent_dir)
                    output_path = write_product_description(parent_dir, input_path, user_format, delivery_files)
                    generate_product_images(parent_dir, delivery_files)
                    sys.stdout.write(f"\n[商品介绍]: 已生成 -> {output_path}\n")
                except Exception as exc:
                    sys.stdout.write(f"\n❌ [商品介绍生成失败]: {exc}\n")
        return

    if os.path.isdir(input_path):
        c_count, s_count, e_count, invalid_count, invalid_files, all_info_texts, product_texts = process_directory_batch(
            input_path,
            user_format,
            scan_only,
            no_archive=no_archive,
        )
        display_batch_summary(c_count, s_count, e_count, invalid_count, invalid_files)

        output_dir = os.path.join(os.getcwd(), "output")
        if not scan_only and (all_info_texts or product_texts):
            # Summary files also use timestamped names, so they are refreshed as a set
            # before we write the current batch results into the shared output folder.
            clear_generated_artifacts(output_dir, remove_image_dirs=False)

        if all_info_texts and not scan_only:
            write_info_summary(output_dir, "📊 批量任务文件信息统计汇总", all_info_texts, "[信息汇总]")

        if product_texts and not scan_only:
            write_product_summary(output_dir, product_texts)


def run_image_generation_workflow(input_path):
    summary = generate_product_images_from_existing_pdfs(input_path)
    if not summary["pdf_found"]:
        sys.stdout.write("\n[商品图片]: 未发现可用的 PDF 文件。\n")
        sys.stdout.write("[商品图片]: images 命令只基于现有 PDF 截图，不包含转换为 PDF。\n")
        return

    sys.stdout.write(f"\n[商品图片]: 已生成图片目录数 -> {summary['generated_count']}\n")
