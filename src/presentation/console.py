import os
import sys

try:
    from tqdm import tqdm
except ImportError:
    sys.stdout.write("[环境异常]: 缺少依赖包 'tqdm'。\n")
    sys.stdout.write("请执行指令进行安装: pip install tqdm\n")
    sys.exit(1)

_active_pbar = None


def display_progress(current, total, current_format, filename):
    global _active_pbar

    if current == 1:
        if _active_pbar is not None:
            _active_pbar.close()

        short_name = filename if len(filename) <= 20 else filename[:17] + "..."
        _active_pbar = tqdm(
            total=total,
            desc=f"处理: {short_name:<20}",
            bar_format="{l_bar}{bar:20}| {n_fmt}/{total_fmt}",
            leave=True,
        )

    if _active_pbar:
        _active_pbar.bar_format = "{l_bar}{bar:20}| {n_fmt}/{total_fmt} [格式: " + f"{current_format}" + "]"
        increment = current - _active_pbar.n
        if increment > 0:
            _active_pbar.update(increment)
        else:
            _active_pbar.refresh()


def display_success(current_format, output_path):
    abs_path = os.path.abspath(output_path)
    clickable_path = f"file:{abs_path.replace(os.sep, '/')}"
    tqdm.write(f"  [保存成功]: {clickable_path}")


def display_scan_result(filename, keywords):
    if keywords:
        sys.stdout.write(f"[结果]: 文件 '{filename}' 发现敏感词: {keywords}\n")
    else:
        sys.stdout.write("[结果]: 内容安全。\n")


def display_error(current_format):
    tqdm.write(f"  [失败]: {current_format} 转换出错。")


def display_final(filename):
    global _active_pbar
    if _active_pbar is not None:
        _active_pbar.close()
        _active_pbar = None
    tqdm.write(f"[完成]: '{filename}' 的任务闭环结束。\n")


def display_archive_success(zip_path):
    sys.stdout.write(f"\n[目录打包完成]: 归档至 {zip_path}\n")
    sys.stdout.flush()


def display_archive_error(dir_path, error_msg):
    sys.stdout.write(f"\n❌ [目录打包失败]: {dir_path} | 异常: {error_msg}\n")
    sys.stdout.flush()


def display_invalid_name(filename):
    sys.stdout.write(f"[命名跳过]: 文件名不符合“作者 - 书名”格式 -> {filename}\n")
    sys.stdout.flush()


def display_batch_summary(compressed_count, skipped_count, error_count, invalid_name_count, invalid_name_files=None):
    invalid_name_files = invalid_name_files or []
    sys.stdout.write(f"\n" + "=" * 40 + "\n")
    sys.stdout.write("[批量任务报告]\n")
    sys.stdout.write(f"  成功归档目录数: {compressed_count}\n")
    sys.stdout.write(f"  跳过目录数: {skipped_count}\n")
    sys.stdout.write(f"  异常目录数: {error_count}\n")
    sys.stdout.write(f"  命名不符合预期数: {invalid_name_count}\n")
    if invalid_name_files:
        sys.stdout.write("  命名不符合预期文件:\n")
        for invalid_file in invalid_name_files:
            sys.stdout.write(f"    - {invalid_file}\n")
    sys.stdout.write("=" * 40 + "\n")
    sys.stdout.flush()
