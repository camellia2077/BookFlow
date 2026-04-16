from pathlib import Path

import pytest

from src.app.main import main


def test_pdf_page_capture_tool_bootstraps_project_root_for_src_import():
    tool_code = compile(
        Path("tools/pdf_page_capture.py").read_text(encoding="utf-8"),
        "tools/pdf_page_capture.py",
        "exec",
    )
    namespace = {"__file__": str(Path("tools/pdf_page_capture.py").resolve()), "__name__": "tool_import_test"}

    exec(tool_code, namespace)

    assert "PROJECT_ROOT" in namespace


def test_cli_returns_error_code_when_input_path_does_not_exist(capsys):
    exit_code = main(["convert", "C:\\definitely-not-exists\\missing.epub"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "找不到输入目标" in captured.out


def test_cli_convert_passes_no_archive_flag(monkeypatch, tmp_path):
    called = {}
    source_dir = tmp_path / "books"
    source_dir.mkdir()

    def fake_run_batch_workflow(input_path, user_format, scan_only=False, no_archive=False):
        called["input_path"] = input_path
        called["user_format"] = user_format
        called["scan_only"] = scan_only
        called["no_archive"] = no_archive

    monkeypatch.setattr("src.app.main.run_batch_workflow", fake_run_batch_workflow)

    exit_code = main(["convert", str(source_dir), "--format", "pdf", "--no-archive"])

    assert exit_code == 0
    assert called == {
        "input_path": str(source_dir),
        "user_format": "pdf",
        "scan_only": False,
        "no_archive": True,
    }


def test_cli_restricts_allowed_format_values():
    with pytest.raises(SystemExit) as exc_info:
        main(["convert", "C:\\books", "--format", "epub"])

    assert exc_info.value.code == 2


def test_cli_images_dispatches_to_image_workflow(monkeypatch, tmp_path):
    called = {}
    source_dir = tmp_path / "books"
    source_dir.mkdir()

    def fake_run_image_generation_workflow(input_path):
        called["input_path"] = input_path

    monkeypatch.setattr("src.app.main.run_image_generation_workflow", fake_run_image_generation_workflow)

    exit_code = main(["images", str(source_dir)])

    assert exit_code == 0
    assert called == {"input_path": str(source_dir)}


def test_image_workflow_explains_when_no_pdf_exists(tmp_path, capsys):
    source_dir = tmp_path / "books"
    source_dir.mkdir()
    (source_dir / "[英] 作者 - 书名.epub").write_text("", encoding="utf-8")

    from src.application.batch_service import run_image_generation_workflow

    run_image_generation_workflow(str(source_dir))

    captured = capsys.readouterr()

    assert "未发现可用的 PDF 文件" in captured.out
    assert "不包含转换为 PDF" in captured.out
