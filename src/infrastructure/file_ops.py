import os
import shutil
import sys

from src.settings import (
    ARCHIVE_EXCLUDED_DIRNAMES,
    ARCHIVE_EXCLUDED_FILE_PREFIXES,
    PRODUCT_IMAGE_MARKER_FILENAME,
)
from src.utils.timestamps import build_timestamped_filename


def is_generated_helper_file(filename):
    return filename.startswith(ARCHIVE_EXCLUDED_FILE_PREFIXES)


def is_program_owned_image_dir(dir_path):
    return os.path.isdir(dir_path) and os.path.exists(os.path.join(dir_path, PRODUCT_IMAGE_MARKER_FILENAME))


def clear_generated_artifacts(dir_path, remove_image_dirs=True):
    if not os.path.isdir(dir_path):
        return

    try:
        for item in os.listdir(dir_path):
            full_path = os.path.join(dir_path, item)

            # Timestamped helper outputs are reproducible, so we clear them first
            # to keep each run idempotent even though filenames no longer overwrite.
            if os.path.isfile(full_path) and is_generated_helper_file(item):
                os.remove(full_path)
                continue

            # Only remove screenshot folders that were created by this program.
            # A manually curated folder with the same visible name should survive cleanup.
            if remove_image_dirs and os.path.isdir(full_path) and item in ARCHIVE_EXCLUDED_DIRNAMES and is_program_owned_image_dir(full_path):
                shutil.rmtree(full_path)
    except Exception as exc:
        sys.stdout.write(f"  [清理警告]: 无法清理生成文件 {dir_path} - {exc}\n")


def collect_target_files(dir_path, target_format):
    target_ext = f".{target_format.lower()}"
    collected = []
    try:
        for item in os.listdir(dir_path):
            full_path = os.path.join(dir_path, item)
            if os.path.isfile(full_path) and os.path.splitext(item)[1].lower() == target_ext:
                collected.append(full_path)
    except Exception:
        return []
    return sorted(collected)


def collect_delivery_files(dir_path):
    delivery_exts = {".pdf", ".txt", ".docx"}
    collected = []
    try:
        for item in os.listdir(dir_path):
            full_path = os.path.join(dir_path, item)
            # Generated helper files should never be mistaken for customer-facing delivery files.
            if is_generated_helper_file(item):
                continue
            if os.path.isfile(full_path) and os.path.splitext(item)[1].lower() in delivery_exts:
                collected.append(full_path)
    except Exception:
        return []
    return sorted(collected)


def collect_pdf_files(dir_path):
    collected = []
    try:
        for item in os.listdir(dir_path):
            full_path = os.path.join(dir_path, item)
            # Image-only mode works from existing PDFs in the original folder,
            # so helper text files are excluded from discovery here as well.
            if is_generated_helper_file(item):
                continue
            if os.path.isfile(full_path) and os.path.splitext(item)[1].lower() == ".pdf":
                collected.append(full_path)
    except Exception:
        return []
    return sorted(collected)


def generate_directory_readme(dir_path, target_exts=None):
    readme_path = os.path.join(dir_path, build_timestamped_filename("文件清单", "txt"))
    lines = []

    try:
        for item in os.listdir(dir_path):
            full_path = os.path.join(dir_path, item)
            if not os.path.isfile(full_path):
                continue

            ext = os.path.splitext(item)[1].lower()
            if target_exts and ext not in target_exts:
                continue

            size_mb = os.path.getsize(full_path) / (1024 * 1024)
            lines.append(f"{item}(约{size_mb:.2f}m)")

        lines.sort()
        content_str = "\n".join(lines) + "\n"
        with open(readme_path, "w", encoding="utf-8") as file_obj:
            file_obj.write(content_str)
        return content_str
    except Exception as exc:
        sys.stdout.write(f"  [警告]: 无法生成目录清单: {exc}\n")
        return ""


def write_info_summary(output_dir, title, contents, success_label):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, build_timestamped_filename("info", "txt"))
    try:
        with open(output_path, "w", encoding="utf-8") as file_obj:
            file_obj.write("=" * 50 + "\n")
            file_obj.write(f"{title}\n")
            file_obj.write("=" * 50 + "\n\n")
            file_obj.write("\n\n".join(contents))
        sys.stdout.write(f"\n{success_label}: 所有清单统计已提取至 -> {output_path}\n")
    except Exception as exc:
        sys.stdout.write(f"\n❌ [信息汇总失败]: 无法写入文件 {output_path} - {exc}\n")


def copy_directory_filtered(source_dir, target_dir):
    try:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        def _ignore(_, names):
            ignored = [name for name in names if is_generated_helper_file(name)]
            # Screenshot folders are internal selling assets and should not be shipped
            # to the buyer when we copy a pure-PDF directory into the archive output.
            ignored.extend(name for name in names if name in ARCHIVE_EXCLUDED_DIRNAMES)
            return ignored

        shutil.copytree(source_dir, target_dir, ignore=_ignore)
        return True, target_dir
    except Exception as exc:
        return False, str(exc)
