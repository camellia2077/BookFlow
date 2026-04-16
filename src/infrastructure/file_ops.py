import os
import shutil
import sys

from src.settings import ARCHIVE_EXCLUDED_FILENAMES


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


def generate_directory_readme(dir_path, target_exts=None):
    readme_path = os.path.join(dir_path, "文件清单.txt")
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


def write_info_summary(output_path, title, contents, success_label):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
            return [name for name in names if name in ARCHIVE_EXCLUDED_FILENAMES]

        shutil.copytree(source_dir, target_dir, ignore=_ignore)
        return True, target_dir
    except Exception as exc:
        return False, str(exc)
