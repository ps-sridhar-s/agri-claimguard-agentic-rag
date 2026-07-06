from pathlib import Path
import re
import os
from dotenv import load_dotenv

load_dotenv()


def clean_filename(filename: str) -> str:
    file_path = Path(filename)

    stem = file_path.stem
    suffix = file_path.suffix.lower()

    stem = stem.replace(" ", "_")
    stem = re.sub(r"[^a-zA-Z0-9_-]", "", stem)
    stem = re.sub(r"_+", "_", stem)

    return f"{stem}{suffix}"


def rename_files() -> list[Path]:
    folder = Path(os.environ["folder_path"])

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    file_paths: list[Path] = []

    for file in folder.rglob("*"):
        if not file.is_file():
            continue

        new_name = clean_filename(file.name)

        # Already valid
        if file.name == new_name:
            file_paths.append(file)
            continue

        new_path = file.parent / new_name

        # Prevent duplicate names
        counter = 1
        while new_path.exists():
            new_path = file.parent / f"{new_path.stem}_{counter}{new_path.suffix}"
            counter += 1

        print(f"Renaming:\n{file.name}\n -> {new_path.name}\n")

        file.rename(new_path)

        # Append the NEW path after renaming
        file_paths.append(new_path)

    return file_paths