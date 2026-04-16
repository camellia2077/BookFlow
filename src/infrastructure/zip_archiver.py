import os
import zipfile

from src.settings import ARCHIVE_EXCLUDED_FILENAMES


def compress_directory(dir_path):
    try:
        zip_path = f"{dir_path}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_obj:
            for root, _, files in os.walk(dir_path):
                for filename in files:
                    if filename in ARCHIVE_EXCLUDED_FILENAMES:
                        continue
                    full_path = os.path.join(root, filename)
                    arcname = os.path.relpath(full_path, dir_path)
                    zip_obj.write(full_path, arcname)
        return True, zip_path
    except Exception as exc:
        return False, str(exc)

