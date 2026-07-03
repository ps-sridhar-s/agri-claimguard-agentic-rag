from pathlib import Path
import re

# Folder path
DATA_FOLDER = Path(
    r"C:\Users\SridharS\Downloads\Sridhar_Project\agri-claimguard-agentic-rag\data_source"
)

def clean_filename(filename: str) -> str:
    """
    Cleans the filename by:
    - Replacing spaces with underscores
    - Removing unwanted special characters
    - Preserving file extension
    """

    file_path = Path(filename)

    stem = file_path.stem
    suffix = file_path.suffix

    # Replace spaces with underscores
    stem = stem.replace(" ", "_")

    # Remove unwanted characters
    # Keeps only letters, numbers, underscores, and hyphens
    stem = re.sub(r"[^a-zA-Z0-9_-]", "", stem)

    # Replace multiple underscores with single underscore
    stem = re.sub(r"_+", "_", stem)

    return f"{stem}{suffix.lower()}"


def rename_files(folder: Path):
    if not folder.exists():
        print(f"Folder does not exist: {folder}")
        return

    for file in folder.rglob("*"):
        if file.is_file():

            new_name = clean_filename(file.name)

            if file.name != new_name:
                new_path = file.parent / new_name

                # Handle duplicate names
                counter = 1
                while new_path.exists():
                    new_name = (
                        f"{Path(new_name).stem}_{counter}"
                        f"{Path(new_name).suffix}"
                    )
                    new_path = file.parent / new_name
                    counter += 1

                print(f"Renaming:\n{file.name}\n -> {new_path.name}\n")

                file.rename(new_path)

    print("✅ File renaming completed.")



