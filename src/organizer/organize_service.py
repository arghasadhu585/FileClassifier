
from pathlib import Path
import shutil
_LAST_OPERATION = []


def organize_files(preview_results, destination_folder, confirm=False):
    """
    Move previewed files into category folders.

    Files move only when confirm=True.
    Existing destination files are never overwritten.
    Successful moves are recorded in memory for undo.
    """
    global _LAST_OPERATION

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

    # Start a fresh undo history for this organization operation.
    _LAST_OPERATION = []

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

                # Do not move a file onto itself.
                if source.resolve() == target.resolve():
                    report["skipped"].append(
                        f"{source.name}: source and destination are the same"
                    )
                    continue

                # Never overwrite an existing destination.
                if target.exists():
                    report["skipped"].append(
                        f"{source.name}: destination already exists"
                    )
                    continue

                shutil.move(str(source), str(target))

                # Record only successful moves.
                _LAST_OPERATION.append({
                    "original": str(source.resolve()),
                    "destination": str(target.resolve()),
                })

                report["moved"].append(
                    f"{source.name} -> {category}/{source.name}"
                )

            except OSError as error:
                report["errors"].append(
                    f"{source.name}: {error}"
                )

    return report


def undo_last_organization():
    """
    Undo the most recent organization operation.

    Files are restored in reverse order to their original locations.
    Existing original files are never overwritten.
    If a file cannot be restored, it is safely skipped with an explanation.

    Note: Undo history is stored in memory only and is lost when
    the application closes.

    Returns a report dictionary with keys:
        - "restored": list of restored file descriptions ("category/file -> file")
        - "skipped": list of skipped file descriptions with reasons
        - "errors": list of error messages for failed moves
    """
    global _LAST_OPERATION

    if not _LAST_OPERATION:
        return {
            "restored": [],
            "skipped": [],
            "errors": [],
        }

    report = {
        "restored": [],
        "skipped": [],
        "errors": [],
    }

    remaining_history = []

    for entry in reversed(_LAST_OPERATION):
        original = Path(entry["original"])
        moved_file = Path(entry["destination"])

        try:
            if not moved_file.exists():
                report["skipped"].append(
                    f"{moved_file.name}: moved file no longer exists at destination"
                )
                continue

            if not moved_file.is_file():
                report["skipped"].append(
                    f"{moved_file.name}: moved path is not a file"
                )
                continue

            # Check if file is already at original location
            if moved_file.resolve() == original.resolve():
                report["skipped"].append(
                    f"{moved_file.name}: file is already at original location"
                )
                continue

            # Never overwrite an existing file at original location
            if original.exists():
                report["skipped"].append(
                    f"{original.name}: original location already contains a file"
                )
                # Keep this record so undo can be retried later if original is cleared
                remaining_history.append(entry)
                continue

            original.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(moved_file), str(original))

            report["restored"].append(
                f"{moved_file.parent.name}/{moved_file.name} -> {original.name}"
            )

        except OSError as error:
            report["errors"].append(
                f"{moved_file.name}: {error}"
            )
            # Keep failed moves in history for a possible retry
            remaining_history.append(entry)

    # Keep only entries that could not be undone.
    _LAST_OPERATION = list(reversed(remaining_history))

    return report


def has_undo_history():
    """
    Check if there is an in-memory undo operation available.

    Returns True if there are recorded file moves that can be undone.
    """
    global _LAST_OPERATION
    return bool(_LAST_OPERATION)


def clear_undo_history():
    """
    Clear the in-memory undo history.
    """
    global _LAST_OPERATION
    _LAST_OPERATION = []


def get_undo_history():
    """
    Return a copy of the current in-memory undo history.
    """
    global _LAST_OPERATION
    return list(_LAST_OPERATION)
