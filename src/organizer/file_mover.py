    
import shutil
from pathlib import Path


def move_file(source_file, destination_folder):
    source = Path(source_file)
    destination = Path(destination_folder)

    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")

    if not destination.exists() or not destination.is_dir():
        raise NotADirectoryError(
            f"Destination folder does not exist: {destination}"
        )

    destination_file = destination / source.name

    if destination_file.exists():
        raise FileExistsError(
            f"File already exists; refusing to overwrite: {destination_file}"
        )

    shutil.move(str(source), str(destination_file))

    return destination_file
