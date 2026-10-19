
from pathlib import Path
from collections import defaultdict
import sys

# Allow this file to use the classifier module
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "src"))

from ..classifier.file_classifier import classify_file


def scan_folder(folder_path):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    files_by_category = defaultdict(list)

    for item in folder.iterdir():
        if item.is_file():
            category = classify_file(item.name)
            files_by_category[category].append(item)

    return files_by_category


if __name__ == "__main__":
    folder_path = input("Enter the folder path to scan: ").strip().strip('"')

    try:
        results = scan_folder(folder_path)
        total_files = 0

        print("\n===== FILE SCAN RESULTS =====")

        for category, files in sorted(results.items()):
            print(f"\n{category} ({len(files)} files)")

            for file_path in files:
                print(f"  - {file_path.name}")
                total_files += 1

        print(f"\nTotal files found: {total_files}")
        print("No files were moved or modified.")

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")
    except PermissionError:
        print("Error: You do not have permission to access this folder.")
