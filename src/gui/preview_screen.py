 
from pathlib import Path
from collections import defaultdict

from ..classifier.file_classifier import classify_file


def generate_preview(folder_path):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Not a folder: {folder}")

    preview = defaultdict(list)

    for item in folder.iterdir():
        if item.is_file():
            category = classify_file(item.name)

            preview[category].append({
                "name": item.name,
                "source": str(item),
                "destination": str(folder / category / item.name),
                "size_bytes": item.stat().st_size,
            })

    return dict(sorted(preview.items()))


def print_preview(preview):
    print("\n========== FILE ORGANIZATION PREVIEW ==========")

    total_files = 0

    for category, files in preview.items():
        print(f"\n{category} ({len(files)} files)")

        for file_info in files:
            size_kb = file_info["size_bytes"] / 1024

            print(f"  File: {file_info['name']}")
            print(f"  Size: {size_kb:.2f} KB")
            print(f"  Planned destination: {file_info['destination']}")
            print()

            total_files += 1

    print(f"Total files in preview: {total_files}")
    print("PREVIEW ONLY — no files have been moved.")


if __name__ == "__main__":
    folder_path = input("Enter the folder path to preview: ").strip().strip('"')

    try:
        preview = generate_preview(folder_path)
        print_preview(preview)
    except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
        print(f"Error: {error}")
