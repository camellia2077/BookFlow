import os
import re


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
    }

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
    return parsed

