import unittest
import tempfile
import shutil
from pathlib import Path

from src.organizer.organize_service import (
    organize_files,
    undo_last_organization,
    has_undo_history,
    clear_undo_history,
    get_undo_history,
)
from src.scanner.folder_scanner import scan_folder
from src.gui.preview_screen import generate_preview


class TestOrganizeService(unittest.TestCase):

    def setUp(self):
        # Create a clean temporary directory for each test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.temp_dir.name)
        clear_undo_history()

    def tearDown(self):
        clear_undo_history()
        self.temp_dir.cleanup()

    def _create_file(self, relative_path, content="test content"):
        full_path = self.test_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return full_path

    # Case 1: Normal organization followed by undo
    def test_normal_organization_followed_by_undo(self):
        f1 = self._create_file("document.txt", "Document text")
        f2 = self._create_file("image.jpg", "Image bytes")

        preview = generate_preview(str(self.test_path))
        self.assertIn("Documents", preview)
        self.assertIn("Images", preview)

        # Organize
        org_report = organize_files(preview, str(self.test_path), confirm=True)
        self.assertEqual(len(org_report["moved"]), 2)
        self.assertEqual(len(org_report["skipped"]), 0)
        self.assertEqual(len(org_report["errors"]), 0)

        # Files moved to category folders
        self.assertFalse(f1.exists())
        self.assertFalse(f2.exists())
        self.assertTrue((self.test_path / "Documents" / "document.txt").exists())
        self.assertTrue((self.test_path / "Images" / "image.jpg").exists())
        self.assertTrue(has_undo_history())

        # Undo
        undo_report = undo_last_organization()
        self.assertEqual(len(undo_report["restored"]), 2)
        self.assertEqual(len(undo_report["skipped"]), 0)
        self.assertEqual(len(undo_report["errors"]), 0)

        # Files restored to original location with original content intact
        self.assertTrue(f1.exists())
        self.assertTrue(f2.exists())
        self.assertEqual(f1.read_text(encoding="utf-8"), "Document text")
        self.assertEqual(f2.read_text(encoding="utf-8"), "Image bytes")

        # Undo history should now be empty
        self.assertFalse(has_undo_history())

    # Case 2: No available undo history
    def test_no_available_undo_history(self):
        clear_undo_history()
        self.assertFalse(has_undo_history())

        report = undo_last_organization()
        self.assertEqual(report["restored"], [])
        self.assertEqual(report["skipped"], [])
        self.assertEqual(report["errors"], [])
        self.assertFalse(has_undo_history())

    # Case 3: Original file location already occupied
    def test_original_file_location_already_occupied(self):
        original_file = self._create_file("notes.txt", "Original notes")

        preview = generate_preview(str(self.test_path))
        organize_files(preview, str(self.test_path), confirm=True)

        moved_file = self.test_path / "Documents" / "notes.txt"
        self.assertTrue(moved_file.exists())
        self.assertFalse(original_file.exists())

        # Put a new file at original location
        original_file.write_text("New notes - do not overwrite!", encoding="utf-8")

        # Run undo
        report = undo_last_organization()

        # Should be safely skipped without overwriting
        self.assertEqual(len(report["restored"]), 0)
        self.assertEqual(len(report["skipped"]), 1)
        self.assertIn("already contains a file", report["skipped"][0])
        self.assertEqual(len(report["errors"]), 0)

        # Verify original file content is intact and was NOT overwritten
        self.assertEqual(original_file.read_text(encoding="utf-8"), "New notes - do not overwrite!")
        # Moved file remains in category folder
        self.assertTrue(moved_file.exists())
        self.assertEqual(moved_file.read_text(encoding="utf-8"), "Original notes")

        # Undo history still retains this entry so it can be retried later
        self.assertTrue(has_undo_history())

        # If user removes the blocking file and retries undo
        original_file.unlink()
        retry_report = undo_last_organization()
        self.assertEqual(len(retry_report["restored"]), 1)
        self.assertTrue(original_file.exists())
        self.assertEqual(original_file.read_text(encoding="utf-8"), "Original notes")
        self.assertFalse(has_undo_history())

    # Case 4: Destination file already exists
    def test_destination_file_already_exists(self):
        source = self._create_file("report.pdf", "Source PDF content")
        # Pre-create the destination file with different content
        dest = self._create_file("Documents/report.pdf", "Existing destination content")

        preview = generate_preview(str(self.test_path))
        report = organize_files(preview, str(self.test_path), confirm=True)

        # report.pdf should be skipped because destination already exists
        self.assertEqual(len(report["moved"]), 0)
        self.assertEqual(len(report["skipped"]), 1)
        self.assertIn("destination already exists", report["skipped"][0])

        # Destination was not overwritten
        self.assertEqual(dest.read_text(encoding="utf-8"), "Existing destination content")
        # Source was not removed
        self.assertTrue(source.exists())
        self.assertEqual(source.read_text(encoding="utf-8"), "Source PDF content")

        # Nothing was moved, so no undo history
        self.assertFalse(has_undo_history())

    # Case 5: Missing source or moved file
    def test_missing_source_file_during_organize(self):
        f = self._create_file("temp.txt", "Temp")
        preview = generate_preview(str(self.test_path))

        # Delete source file before organizing
        f.unlink()

        report = organize_files(preview, str(self.test_path), confirm=True)
        self.assertEqual(len(report["moved"]), 0)
        self.assertEqual(len(report["skipped"]), 1)
        self.assertIn("source file no longer exists", report["skipped"][0])
        self.assertFalse(has_undo_history())

    def test_missing_moved_file_during_undo(self):
        self._create_file("temp.txt", "Temp")
        preview = generate_preview(str(self.test_path))
        organize_files(preview, str(self.test_path), confirm=True)

        moved_file = self.test_path / "Documents" / "temp.txt"
        self.assertTrue(moved_file.exists())

        # User deletes moved file externally before undo
        moved_file.unlink()

        report = undo_last_organization()
        self.assertEqual(len(report["restored"]), 0)
        self.assertEqual(len(report["skipped"]), 1)
        self.assertIn("no longer exists at destination", report["skipped"][0])
        self.assertEqual(len(report["errors"]), 0)
        # Entry should not remain in history since file is gone
        self.assertFalse(has_undo_history())

    # Case 6: Empty folder
    def test_empty_folder(self):
        scanned = scan_folder(str(self.test_path))
        self.assertEqual(len(scanned), 0)

        preview = generate_preview(str(self.test_path))
        self.assertEqual(len(preview), 0)

        report = organize_files(preview, str(self.test_path), confirm=True)
        self.assertEqual(report["moved"], [])
        self.assertEqual(report["skipped"], [])
        self.assertEqual(report["errors"], [])
        self.assertFalse(has_undo_history())

        undo_report = undo_last_organization()
        self.assertEqual(undo_report["restored"], [])
        self.assertEqual(undo_report["skipped"], [])
        self.assertEqual(undo_report["errors"], [])

    # Case 7: Multiple file categories
    def test_multiple_file_categories(self):
        files_data = {
            "pic.jpg": ("Images", "image data"),
            "doc.docx": ("Documents", "doc data"),
            "video.mp4": ("Videos", "video data"),
            "song.mp3": ("Audio", "audio data"),
            "script.py": ("Code", "print('hello')"),
            "sheet.csv": ("Spreadsheets", "a,b,c"),
            "archive.zip": ("Archives", "zip data"),
            "unknown.abc": ("Others", "unknown data"),
        }

        created_paths = {}
        for filename, (expected_cat, content) in files_data.items():
            created_paths[filename] = self._create_file(filename, content)

        preview = generate_preview(str(self.test_path))
        self.assertEqual(len(preview), len(files_data))

        # Check each file was correctly classified in preview
        for filename, (expected_cat, _) in files_data.items():
            self.assertIn(expected_cat, preview)
            cat_files = [item["name"] for item in preview[expected_cat]]
            self.assertIn(filename, cat_files)

        # Organize
        org_report = organize_files(preview, str(self.test_path), confirm=True)
        self.assertEqual(len(org_report["moved"]), len(files_data))
        self.assertEqual(len(org_report["skipped"]), 0)
        self.assertEqual(len(org_report["errors"]), 0)

        # Verify each file is in its category directory
        for filename, (expected_cat, content) in files_data.items():
            moved = self.test_path / expected_cat / filename
            self.assertTrue(moved.exists(), f"Expected {moved} to exist")
            self.assertEqual(moved.read_text(encoding="utf-8"), content)
            self.assertFalse(created_paths[filename].exists())

        # Undo
        undo_report = undo_last_organization()
        self.assertEqual(len(undo_report["restored"]), len(files_data))
        self.assertEqual(len(undo_report["skipped"]), 0)
        self.assertEqual(len(undo_report["errors"]), 0)

        # Verify all files are restored to root with intact content
        for filename, (_, content) in files_data.items():
            restored = created_paths[filename]
            self.assertTrue(restored.exists(), f"Expected {restored} to be restored")
            self.assertEqual(restored.read_text(encoding="utf-8"), content)

        self.assertFalse(has_undo_history())

    # Case 8: Invalid folder paths
    def test_invalid_folder_paths(self):
        non_existent_folder = self.test_path / "non_existent_directory"
        file_path = self._create_file("not_a_folder.txt", "I am a file")

        # organize_files with non-existent destination
        with self.assertRaises(NotADirectoryError):
            organize_files({}, str(non_existent_folder), confirm=True)

        # organize_files with destination that is a file
        with self.assertRaises(NotADirectoryError):
            organize_files({}, str(file_path), confirm=True)

        # organize_files without confirmation
        with self.assertRaises(PermissionError):
            organize_files({}, str(self.test_path), confirm=False)

        # scan_folder with non-existent path
        with self.assertRaises(FileNotFoundError):
            scan_folder(str(non_existent_folder))

        # scan_folder with file path instead of folder
        with self.assertRaises(NotADirectoryError):
            scan_folder(str(file_path))

        # generate_preview with non-existent path
        with self.assertRaises(FileNotFoundError):
            generate_preview(str(non_existent_folder))

        # generate_preview with file path instead of folder
        with self.assertRaises(NotADirectoryError):
            generate_preview(str(file_path))


if __name__ == "__main__":
    unittest.main()
