from pathlib import Path

from src.safe_file_renamer import clean_filename, rename_files


def test_clean_filename_removes_invalid_characters():
    cleaned = clean_filename("My File!?@#.txt")
    assert cleaned == "My_File.txt"


def test_rename_files_applies_clean_names(tmp_path, monkeypatch):
    folder = tmp_path
    original = folder / "My File #1.txt"
    original.write_text("hello world", encoding="utf-8")

    monkeypatch.setenv("folder_path", str(folder))
    renamed_paths = rename_files()

    assert any(path.name == "My_File_1.txt" for path in renamed_paths)
    assert (folder / "My_File_1.txt").exists()
