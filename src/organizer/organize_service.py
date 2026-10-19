
from pathlib import Path
import shutil


def organize_files(preview_results, destination_folder, confirm=False):
    """
    Move previewed files into category folders.

    Files are moved only when confirm=True.
    Existing destination files are never overwritten.
    """

    if not confirm:
        raise PermissionError(
            "Organization was not confirmed. No files were moved."
        )

    destination = Path(destination_folder).resolve()

    if not destination.exists() or not destination.is_dir():
        raise NotADirectoryError(
            f"Destination folder does not exist: {destination}"
        )

    report = {
        "moved": [],
        "skipped": [],
        "errors": [],
    }

    for category, files in preview_results.items():
        category_folder = destination / category

        try:
            category_folder.mkdir(exist_ok=True)
        except OSError as error:
            report["errors"].append(
                f"Could not create {category_folder}: {error}"
            )
            continue

        for item in files:
            source = Path(item["source"])
            target = category_folder / source.name

            try:
                if not source.exists() or not source.is_file():
                    report["skipped"].append(
                        f"{source.name}: source file no longer exists"
                    )
                    continue

                if source.resolve() == target.resolve():
                    report["skipped"].append(
                        f"{source.name}: source and destination are the same"
                    )
                    continue

                if target.exists():
                    report["skipped"].append(
                        f"{source.name}: destination already exists"
                    )
                    continue

                shutil.move(str(source), str(target))
                report["moved"].append(
                    f"{source.name} -> {category}/{source.name}"
                )

            except OSError as error:
                report["errors"].append(
                    f"{source.name}: {error}"
                )

    return report
