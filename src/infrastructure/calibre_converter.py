import os
import subprocess
import zipfile

from src.settings import CALIBRE_PATH, FORBIDDEN_KEYWORDS


def check_environment():
    if not os.path.exists(CALIBRE_PATH):
        raise FileNotFoundError(f"未找到 Calibre 转换引擎于 {CALIBRE_PATH}")
    return CALIBRE_PATH


def _search_keywords(text):
    return [word for word in FORBIDDEN_KEYWORDS if word in text]


def _scan_zip_container(path):
    found = []
    with zipfile.ZipFile(path, "r") as zip_obj:
        targets = [file_info for file_info in zip_obj.infolist() if file_info.filename.endswith((".html", ".htm", ".xhtml", ".xml", ".txt"))]
        for file_info in targets:
            with zip_obj.open(file_info) as file_obj:
                content = file_obj.read().decode("utf-8", errors="ignore")
                found.extend(_search_keywords(content))
    return found


def _scan_binary_fallback(path):
    with open(path, "rb") as file_obj:
        content = file_obj.read().decode("utf-8", errors="ignore")
        return _search_keywords(content)


def validate_content(input_path):
    ext = os.path.splitext(input_path)[1].lower()
    try:
        if ext in [".epub", ".docx"]:
            results = _scan_zip_container(input_path)
        elif ext in [".mobi", ".azw3"]:
            results = _scan_binary_fallback(input_path)
        else:
            results = []
        return list(set(results))
    except Exception:
        return []


def run_conversion_task(engine_path, input_path, output_path, target_format):
    command = [engine_path, input_path, output_path]
    if target_format.lower() == "pdf":
        command.extend(["--paper-size", "a4", "--pdf-default-font-size", "12"])
    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

