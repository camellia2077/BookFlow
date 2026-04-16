from src.domain.book_parser import normalize_book_title, parse_book_filename


def test_normalize_book_title_removes_extra_spaces_around_plus():
    assert normalize_book_title("帝国的背影：土耳其简史 + 哈布斯堡王朝") == "帝国的背影：土耳其简史+哈布斯堡王朝"


def test_parse_book_filename_extracts_authors_and_title():
    result = parse_book_filename("[英] 诺曼·斯通, [美] 彼得·贾德森 - 帝国的背影：土耳其简史 + 哈布斯堡王朝.epub")

    assert result["is_expected_format"] is True
    assert result["authors"] == ["诺曼·斯通", "彼得·贾德森"]
    assert result["title"] == "帝国的背影：土耳其简史+哈布斯堡王朝"


def test_parse_book_filename_marks_unexpected_format():
    result = parse_book_filename("不符合格式的文件名.epub")

    assert result["is_expected_format"] is False
    assert result["authors"] == []
    assert result["title"] == "不符合格式的文件名"

