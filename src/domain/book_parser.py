import os
import re


ASCII_BOOK_TEXT_PATTERN = re.compile(r"^[A-Za-z0-9\s\.,:;!'\"()\[\]\-_/&+]+$")


def normalize_book_title(title):
    normalized = re.sub(r"\s*[+＋]\s*", "+", title.strip())
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def parse_book_filename(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0].strip()
    parsed = {
        "raw_name": base_name,
        "title": base_name,
        "authors": [],
        "is_expected_format": False,
    }

    # This parser intentionally accepts only the seller's canonical
    # "author - title" pattern so the rest of the automation can stay deterministic.
    if " - " not in base_name:
        parsed["title"] = normalize_book_title(base_name)
        return parsed

    author_part, title_part = base_name.split(" - ", 1)
    title = normalize_book_title(title_part)

    authors = []
    for author in re.split(r"[,，、]+", author_part):
        cleaned = re.sub(r"\[[^\]]+\]\s*", "", author).strip()
        if cleaned:
            authors.append(cleaned)

    parsed["title"] = title or base_name
    parsed["authors"] = authors
    parsed["is_expected_format"] = bool(title and authors)
    return parsed


def is_obviously_english_named_book(file_path):
    parsed = parse_book_filename(file_path)
    if not parsed["is_expected_format"]:
        return False

    raw_name = parsed["raw_name"]
    if re.search(r"[\u4e00-\u9fff]", raw_name):
        return False

    english_fields = [parsed["title"], *parsed["authors"]]
    return all(field and ASCII_BOOK_TEXT_PATTERN.match(field) for field in english_fields)
