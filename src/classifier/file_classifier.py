
from pathlib import Path
from .extension_rules import EXTENSION_CATEGORIES


def classify_file(filename):
    extension = Path(filename).suffix.lower()
    return EXTENSION_CATEGORIES.get(extension, "Others")


if __name__ == "__main__":
    sample_files = [
        "photo.jpg",
        "report.pdf",
        "movie.mp4",
        "song.mp3",
        "program.py",
        "data.xlsx",
        "backup.zip",
        "unknown.xyz",
        "README",
    ]

    print("File Classification Results")
    print("-" * 35)

    for filename in sample_files:
        category = classify_file(filename)
        print(f"{filename} -> {category}")
