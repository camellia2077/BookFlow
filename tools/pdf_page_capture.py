import sys
from pathlib import Path

import fitz

# Direct script execution starts from tools/, so we prepend the repository root
# to sys.path and keep imports consistent with the main application package.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.settings import PRODUCT_IMAGE_SCALE
from src.utils.timestamps import get_beijing_timestamp_for_filename

# Update this path before running the script.
PDF_PATH = Path(r"C:\REDACTED\book.pdf")

# Page numbers are 1-based here for easier manual editing.
PAGE_NUMBERS = [8]


def render_selected_pages(pdf_path: Path, page_numbers: list[int]) -> list[Path]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_paths: list[Path] = []
    timestamp = get_beijing_timestamp_for_filename()

    with fitz.open(pdf_path) as doc:
        if len(doc) == 0:
            return []

        matrix = fitz.Matrix(PRODUCT_IMAGE_SCALE, PRODUCT_IMAGE_SCALE)

        for page_number in page_numbers:
            if page_number < 1 or page_number > len(doc):
                raise ValueError(f"Page {page_number} is out of range. Valid range: 1-{len(doc)}")

            page = doc[page_number - 1]
            output_path = pdf_path.parent / f"page_{page_number:03d}_{timestamp}.png"
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pixmap.save(output_path)
            output_paths.append(output_path)

    return output_paths


def main():
    output_paths = render_selected_pages(PDF_PATH, PAGE_NUMBERS)
    if not output_paths:
        print("No images generated.")
        return

    print("Generated images:")
    for path in output_paths:
        print(path)


if __name__ == "__main__":
    main()
