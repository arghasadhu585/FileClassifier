
from pathlib import Path


def create_category_folders(destination_folder, categories):
    destination = Path(destination_folder)

    if not destination.exists():
        raise FileNotFoundError(
            f"Destination folder does not exist: {destination}"
        )

    if not destination.is_dir():
        raise NotADirectoryError(
            f"Destination is not a folder: {destination}"
        )

    created_folders = []

    for category in sorted(set(categories)):
        category_folder = destination / category

        if category_folder.exists():
            if not category_folder.is_dir():
                raise FileExistsError(
                    f"A file already exists with this name: {category_folder}"
                )
        else:
            category_folder.mkdir()
            created_folders.append(category_folder)

    return created_folders
