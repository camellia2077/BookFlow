import os
import zipfile

from src.infrastructure.file_ops import is_generated_helper_file
from src.settings import ARCHIVE_EXCLUDED_DIRNAMES, ZIP_COMPRESSION_LEVEL


def compress_directory(dir_path):
    try:
        zip_path = f"{dir_path}.zip"
        with zipfile.ZipFile(
            zip_path,
            "w",
            zipfile.ZIP_DEFLATED,
            compresslevel=ZIP_COMPRESSION_LEVEL,
        ) as zip_obj:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [dir_name for dir_name in dirs if dir_name not in ARCHIVE_EXCLUDED_DIRNAMES]
                for filename in files:
                    if is_generated_helper_file(filename):
                        continue
                    full_path = os.path.join(root, filename)
                    arcname = os.path.relpath(full_path, dir_path)
                    zip_obj.write(full_path, arcname)
        return True, zip_path
    except Exception as exc:
        return False, str(exc)
