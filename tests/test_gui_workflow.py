import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import customtkinter as ctk

from src.gui.main_window import FileClassifierApp
from src.organizer.organize_service import clear_undo_history, has_undo_history


class TestGUIWorkflow(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.temp_dir.name)
        clear_undo_history()

        # Instantiate app but withdraw window so it does not pop up
        self.app = FileClassifierApp()
        self.app.withdraw()

    def tearDown(self):
        clear_undo_history()
        try:
            self.app.update_idletasks()
            self.app.destroy()
        except Exception:
            pass
        self.temp_dir.cleanup()

    def _create_file(self, relative_path, content="gui test"):
        full_path = self.test_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return full_path

    def test_gui_undo_button_exists(self):
        """Verify the 'Undo Last Organization' button exists in the GUI."""
        found = False
        for child in self.app.winfo_children():
            # Check frames
            if isinstance(child, ctk.CTkFrame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkFrame):
                        for btn in subchild.winfo_children():
                            if isinstance(btn, ctk.CTkButton) and "Undo" in btn.cget("text"):
                                found = True
                                self.assertEqual(btn.cget("text"), "Undo Last Organization")
                                break
        self.assertTrue(found, "Undo Last Organization button not found in GUI")

    @patch("src.gui.main_window.messagebox.showinfo")
    @patch("src.gui.main_window.messagebox.askyesno")
    def test_gui_undo_no_history_shows_message(self, mock_askyesno, mock_showinfo):
        """Clicking Undo when no history is present should show a helpful info message and NOT ask confirmation."""
        self.assertFalse(has_undo_history())
        self.app.undo_organization()

        mock_showinfo.assert_called_once()
        args, _ = mock_showinfo.call_args
        self.assertIn("No Undo Available", args[0])
        self.assertIn("no organization operation available to undo", args[1].lower())
        mock_askyesno.assert_not_called()

    @patch("src.gui.main_window.undo_last_organization")
    @patch("src.gui.main_window.has_undo_history", return_value=True)
    @patch("src.gui.main_window.messagebox.askyesno", return_value=False)
    def test_gui_undo_confirmation_cancelled(self, mock_askyesno, mock_has_undo, mock_undo_func):
        """Clicking Undo but selecting No on the confirmation dialog should abort the undo."""
        self.app.undo_organization()

        mock_askyesno.assert_called_once()
        mock_undo_func.assert_not_called()

    @patch("src.gui.main_window.messagebox.showinfo")
    @patch("src.gui.main_window.messagebox.askyesno", return_value=True)
    def test_gui_full_organize_and_undo_flow(self, mock_askyesno, mock_showinfo):
        """Test full GUI flow: select folder -> preview -> confirm -> undo -> verify refreshed."""
        f1 = self._create_file("document.txt", "doc data")
        f2 = self._create_file("photo.jpg", "image data")

        self.app.selected_folder = str(self.test_path)
        self.app.folder_label.configure(text=str(self.test_path))

        # Preview organization
        self.app.preview_organization()
        self.assertIn("Documents", self.app.preview_results)
        self.assertIn("Images", self.app.preview_results)

        # Confirm organization
        self.app.confirm_preview()
        mock_askyesno.assert_called()
        self.assertTrue(has_undo_history())
        self.assertFalse(f1.exists())
        self.assertFalse(f2.exists())
        self.assertTrue((self.test_path / "Documents" / "document.txt").exists())
        self.assertTrue((self.test_path / "Images" / "photo.jpg").exists())
        self.assertIn("Organization finished", self.app.status_label.cget("text"))

        # Now Undo organization
        mock_askyesno.reset_mock()
        mock_showinfo.reset_mock()

        self.app.undo_organization()
        mock_askyesno.assert_called_once()
        mock_showinfo.assert_called()
        self.assertFalse(has_undo_history())

        # Files restored
        self.assertTrue(f1.exists())
        self.assertTrue(f2.exists())
        self.assertIn("Undo finished", self.app.status_label.cget("text"))

    @patch("src.gui.main_window.messagebox.showerror")
    @patch("src.gui.main_window.has_undo_history", return_value=True)
    @patch("src.gui.main_window.messagebox.askyesno", return_value=True)
    @patch("src.gui.main_window.undo_last_organization", side_effect=PermissionError("Simulated access denied"))
    def test_gui_undo_handles_errors_gracefully(self, mock_undo, mock_askyesno, mock_has_undo, mock_showerror):
        """Undo error should trigger showerror dialog without crashing the application."""
        self.app.undo_organization()
        mock_showerror.assert_called_once()
        title, message = mock_showerror.call_args[0]
        self.assertEqual(title, "Undo Error")
        self.assertIn("Simulated access denied", message)


if __name__ == "__main__":
    unittest.main()
