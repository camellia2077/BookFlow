from pathlib import Path

from src.application import batch_service


def test_invalid_name_count_increases_for_unexpected_filename(tmp_path: Path):
    bad_file = tmp_path / "不符合格式.epub"
    bad_file.write_text("", encoding="utf-8")

    compressed_count, skipped_count, error_count, invalid_name_count, invalid_name_files, _, _ = batch_service.process_directory_batch(
        str(tmp_path),
        "pdf",
        scan_only=False,
    )

    assert compressed_count == 0
    assert invalid_name_count == 1
    assert error_count == 0
    assert invalid_name_files == [str(bad_file)]


def test_batch_summary_prints_invalid_filenames(tmp_path: Path, capsys):
    bad_file = tmp_path / "不符合格式.epub"
    bad_file.write_text("", encoding="utf-8")

    batch_service.run_batch_workflow(str(tmp_path), user_format="pdf", scan_only=False)

    captured = capsys.readouterr()

    assert "命名不符合预期数: 1" in captured.out
    assert "命名不符合预期文件:" in captured.out
    assert str(bad_file) in captured.out


def test_pure_pdf_directory_is_copied_and_not_counted_as_skipped(tmp_path: Path):
    source_dir = tmp_path / "纯PDF目录"
    source_dir.mkdir()
    (source_dir / "[英] 作者 - 书名.pdf").write_text("pdf", encoding="utf-8")

    compressed_count, skipped_count, error_count, invalid_name_count, _, _, _ = batch_service.process_directory_batch(
        str(tmp_path),
        "pdf",
        scan_only=False,
    )

    copied_dir = tmp_path.parent / f"{tmp_path.name}_输出归档" / "纯PDF目录"

    assert compressed_count == 1
    assert skipped_count == 0
    assert error_count == 0
    assert invalid_name_count == 0
    assert copied_dir.exists()
    assert (copied_dir / "[英] 作者 - 书名.pdf").exists()


def test_batch_run_rebuilds_archive_output_directory_from_scratch(tmp_path: Path):
    source_dir = tmp_path / "纯PDF目录"
    source_dir.mkdir()
    (source_dir / "[英] 作者 - 书名.pdf").write_text("pdf", encoding="utf-8")

    archive_dir = tmp_path.parent / f"{tmp_path.name}_输出归档"
    archive_dir.mkdir()
    stale_dir = archive_dir / "旧目录"
    stale_dir.mkdir()
    (stale_dir / "stale.txt").write_text("old", encoding="utf-8")

    batch_service.process_directory_batch(str(tmp_path), "pdf", scan_only=False)

    assert not stale_dir.exists()
    assert (archive_dir / "纯PDF目录").exists()


def test_failed_conversion_does_not_create_archive_and_counts_as_skipped(tmp_path: Path, monkeypatch):
    source_dir = tmp_path / "需要转换"
    source_dir.mkdir()
    (source_dir / "[英] 作者 - 书名.epub").write_text("", encoding="utf-8")

    monkeypatch.setattr(batch_service, "_get_engine", lambda: "fake-engine")
    monkeypatch.setattr(batch_service, "validate_content", lambda _: [])
    monkeypatch.setattr(batch_service, "run_conversion_task", lambda *args, **kwargs: False)

    compressed_count, skipped_count, error_count, invalid_name_count, _, _, _ = batch_service.process_directory_batch(
        str(tmp_path),
        "pdf",
        scan_only=False,
    )

    archive_dir = tmp_path.parent / f"{tmp_path.name}_输出归档"

    assert compressed_count == 0
    assert skipped_count == 1
    assert error_count == 0
    assert invalid_name_count == 0
    assert not any(archive_dir.glob("*.zip"))


def test_successful_conversion_writes_product_summary(tmp_path: Path, monkeypatch):
    source_dir = tmp_path / "books"
    source_dir.mkdir()
    input_file = source_dir / "[英] 作者 - 书名.epub"
    input_file.write_text("", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    def fake_run_conversion_task(_engine, _input_path, output_path, target_format):
        output = Path(output_path)
        if target_format == "pdf":
            from pypdf import PdfWriter

            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            with open(output, "wb") as file_obj:
                writer.write(file_obj)
        elif target_format == "txt":
            output.write_text("generated\n", encoding="utf-8")
        else:
            output.write_bytes(b"docx")
        return True

    monkeypatch.setattr(batch_service, "_get_engine", lambda: "fake-engine")
    monkeypatch.setattr(batch_service, "validate_content", lambda _: [])
    monkeypatch.setattr(batch_service, "run_conversion_task", fake_run_conversion_task)

    batch_service.run_batch_workflow(str(source_dir), user_format="pdf", scan_only=False)

    summary_dir = tmp_path / "output"
    summary_files = list(summary_dir.glob("商品介绍汇总_*.txt"))

    assert len(summary_files) == 1
    assert "书名 作者 PDF/TXT/DOCX/EPUB格式共（1）套" in summary_files[0].read_text(encoding="utf-8")


def test_no_archive_converts_without_creating_archive_output(tmp_path: Path, monkeypatch):
    source_dir = tmp_path / "books"
    source_dir.mkdir()
    input_file = source_dir / "[英] 作者 - 书名.epub"
    input_file.write_text("", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    def fake_run_conversion_task(_engine, _input_path, output_path, target_format):
        output = Path(output_path)
        if target_format == "pdf":
            from pypdf import PdfWriter

            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            with open(output, "wb") as file_obj:
                writer.write(file_obj)
        elif target_format == "txt":
            output.write_text("generated\n", encoding="utf-8")
        else:
            output.write_bytes(b"docx")
        return True

    monkeypatch.setattr(batch_service, "_get_engine", lambda: "fake-engine")
    monkeypatch.setattr(batch_service, "validate_content", lambda _: [])
    monkeypatch.setattr(batch_service, "run_conversion_task", fake_run_conversion_task)

    batch_service.run_batch_workflow(str(source_dir), user_format="pdf", scan_only=False, no_archive=True)

    archive_dir = tmp_path / "books_输出归档"

    assert not archive_dir.exists()
    assert len(list(source_dir.glob("商品介绍_*.txt"))) == 1


def test_processing_cleans_old_generated_directory_files_before_rewriting(tmp_path: Path):
    source_dir = tmp_path / "纯PDF目录"
    source_dir.mkdir()
    pdf_path = source_dir / "[英] 作者 - 书名.pdf"
    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(7):
        writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as file_obj:
        writer.write(file_obj)
    (source_dir / "商品介绍_2026-04-16T10-00-00+08-00.txt").write_text("old intro", encoding="utf-8")
    (source_dir / "文件清单_2026-04-16T10-00-00+08-00.txt").write_text("old list", encoding="utf-8")
    image_dir = source_dir / "商品图片"
    image_dir.mkdir()
    (image_dir / ".bookflow-generated").write_text("Generated by BookFlow.\n", encoding="utf-8")
    (image_dir / "01_封面_2026-04-16T10-00-00+08-00.png").write_text("old image", encoding="utf-8")

    batch_service.process_directory_batch(str(tmp_path), "pdf", scan_only=False)

    assert len(list(source_dir.glob("商品介绍_*.txt"))) == 1
    assert len(list(source_dir.glob("文件清单_*.txt"))) == 1
    assert len(list((source_dir / "商品图片").glob("*.png"))) >= 1
    assert not (source_dir / "商品介绍_2026-04-16T10-00-00+08-00.txt").exists()
    assert not (source_dir / "文件清单_2026-04-16T10-00-00+08-00.txt").exists()
    assert not (source_dir / "商品图片" / "01_封面_2026-04-16T10-00-00+08-00.png").exists()


def test_image_workflow_generates_images_in_original_directory(tmp_path: Path):
    source_dir = tmp_path / "books"
    source_dir.mkdir()
    pdf_path = source_dir / "[英] 作者 - 书名.pdf"

    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(7):
        writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as file_obj:
        writer.write(file_obj)

    summary = batch_service.generate_product_images_from_existing_pdfs(str(source_dir))

    image_dir = source_dir / "商品图片"

    assert summary == {"generated_count": 1, "pdf_found": True}
    assert image_dir.exists()
    assert len(list(image_dir.glob("01_封面_*.png"))) == 1


def test_image_workflow_cleans_old_generated_artifacts_before_rendering(tmp_path: Path):
    source_dir = tmp_path / "books"
    source_dir.mkdir()
    pdf_path = source_dir / "[英] 作者 - 书名.pdf"

    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(7):
        writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as file_obj:
        writer.write(file_obj)

    (source_dir / "商品介绍_2026-04-16T10-00-00+08-00.txt").write_text("old intro", encoding="utf-8")
    image_dir = source_dir / "商品图片"
    image_dir.mkdir()
    (image_dir / ".bookflow-generated").write_text("Generated by BookFlow.\n", encoding="utf-8")
    (image_dir / "01_封面_2026-04-16T10-00-00+08-00.png").write_text("old image", encoding="utf-8")

    summary = batch_service.generate_product_images_from_existing_pdfs(str(source_dir))

    assert summary == {"generated_count": 1, "pdf_found": True}
    assert not (source_dir / "商品介绍_2026-04-16T10-00-00+08-00.txt").exists()
    assert not (source_dir / "商品图片" / "01_封面_2026-04-16T10-00-00+08-00.png").exists()
    assert len(list((source_dir / "商品图片").glob("*.png"))) >= 1


def test_image_workflow_keeps_manual_image_folder_without_marker(tmp_path: Path):
    source_dir = tmp_path / "books"
    source_dir.mkdir()
    pdf_path = source_dir / "[英] 作者 - 书名.pdf"

    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(7):
        writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as file_obj:
        writer.write(file_obj)

    image_dir = source_dir / "商品图片"
    image_dir.mkdir()
    (image_dir / "manual-note.txt").write_text("keep", encoding="utf-8")

    summary = batch_service.generate_product_images_from_existing_pdfs(str(source_dir))

    assert summary == {"generated_count": 1, "pdf_found": True}
    assert (image_dir / "manual-note.txt").exists()
    assert (image_dir / ".bookflow-generated").exists()


def test_successful_batch_cleans_old_output_summaries(tmp_path: Path, monkeypatch):
    source_dir = tmp_path / "books"
    source_dir.mkdir()
    input_file = source_dir / "[英] 作者 - 书名.epub"
    input_file.write_text("", encoding="utf-8")

    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "info_2026-04-16T10-00-00+08-00.txt").write_text("old info", encoding="utf-8")
    (output_dir / "商品介绍汇总_2026-04-16T10-00-00+08-00.txt").write_text("old summary", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    def fake_run_conversion_task(_engine, _input_path, output_path, target_format):
        output = Path(output_path)
        if target_format == "pdf":
            from pypdf import PdfWriter

            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            with open(output, "wb") as file_obj:
                writer.write(file_obj)
        elif target_format == "txt":
            output.write_text("generated\n", encoding="utf-8")
        else:
            output.write_bytes(b"docx")
        return True

    monkeypatch.setattr(batch_service, "_get_engine", lambda: "fake-engine")
    monkeypatch.setattr(batch_service, "validate_content", lambda _: [])
    monkeypatch.setattr(batch_service, "run_conversion_task", fake_run_conversion_task)

    batch_service.run_batch_workflow(str(source_dir), user_format="pdf", scan_only=False)

    assert len(list(output_dir.glob("info_*.txt"))) == 1
    assert len(list(output_dir.glob("商品介绍汇总_*.txt"))) == 1
    assert not (output_dir / "info_2026-04-16T10-00-00+08-00.txt").exists()
    assert not (output_dir / "商品介绍汇总_2026-04-16T10-00-00+08-00.txt").exists()
