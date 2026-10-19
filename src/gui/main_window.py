
import customtkinter as ctk
from tkinter import filedialog, messagebox

from ..scanner.folder_scanner import scan_folder
from ..gui.preview_screen import generate_preview
from ..organizer.organize_service import organize_files


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FileClassifierApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("FileClassifier")
        self.geometry("1050x720")
        self.minsize(850, 600)

        self.selected_folder = None
        self.scan_results = {}
        self.preview_results = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_header()
        self.create_main_area()
        self.create_footer()

    # ---------------- HEADER ----------------

    def create_header(self):
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="FileClassifier",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=25, pady=(20, 0), sticky="w")

        ctk.CTkLabel(
            header,
            text="Scan, preview, and organize your files safely.",
            font=ctk.CTkFont(size=14)
        ).grid(row=1, column=0, padx=25, pady=(5, 20), sticky="w")

    # ---------------- MAIN AREA ----------------

    def create_main_area(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, padx=25, pady=20, sticky="nsew")

        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(3, weight=1)

        # Folder selection
        folder_frame = ctk.CTkFrame(main)
        folder_frame.grid(
            row=0, column=0, sticky="ew", pady=(0, 15)
        )
        folder_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            folder_frame,
            text="SELECT A FOLDER",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.folder_label = ctk.CTkLabel(
            folder_frame,
            text="No folder selected",
            anchor="w",
            wraplength=700
        )
        self.folder_label.grid(
            row=1, column=0, padx=15, pady=(0, 15), sticky="ew"
        )

        ctk.CTkButton(
            folder_frame,
            text="Browse Folder",
            command=self.choose_folder
        ).grid(row=0, column=1, rowspan=2, padx=15, pady=15)

        # Action buttons
        button_frame = ctk.CTkFrame(main, fg_color="transparent")
        button_frame.grid(
            row=1, column=0, sticky="ew", pady=(0, 15)
        )
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame,
            text="Scan Folder",
            height=42,
            command=self.scan_selected_folder
        ).grid(row=0, column=0, padx=(0, 7), sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Preview Organization",
            height=42,
            command=self.preview_organization
        ).grid(row=0, column=1, padx=(7, 0), sticky="ew")

        # Status
        self.status_label = ctk.CTkLabel(
            main,
            text="Select a folder to begin.",
            anchor="w"
        )
        self.status_label.grid(
            row=2, column=0, sticky="ew", pady=(0, 10)
        )

        # Results area
        self.results_frame = ctk.CTkScrollableFrame(
            main,
            label_text="FILE RESULTS"
        )
        self.results_frame.grid(
            row=3, column=0, sticky="nsew"
        )

        self.show_empty_state()

    # ---------------- FOOTER ----------------

    def create_footer(self):
        ctk.CTkLabel(
            self,
            text="Review the preview before confirming file movement.",
            font=ctk.CTkFont(size=12)
        ).grid(row=2, column=0, padx=20, pady=(0, 15))

    # ---------------- EMPTY STATE ----------------

    def show_empty_state(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.results_frame,
            text="Choose a folder and scan or preview its files.",
            font=ctk.CTkFont(size=15)
        ).pack(padx=20, pady=30)

    # ---------------- SELECT FOLDER ----------------

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Choose a folder to organize"
        )

        if folder:
            self.selected_folder = folder
            self.scan_results = {}
            self.preview_results = {}

            self.folder_label.configure(text=folder)
            self.status_label.configure(
                text="Folder selected. Scan or preview it."
            )
            self.show_empty_state()

    # ---------------- SCAN ----------------

    def scan_selected_folder(self):
        if not self.selected_folder:
            messagebox.showwarning(
                "No folder selected",
                "Please select a folder first."
            )
            return

        try:
            self.scan_results = scan_folder(self.selected_folder)
            self.preview_results = {}

            self.display_scan_results()
            self.status_label.configure(text="Scan completed.")

        except (OSError, ValueError) as error:
            messagebox.showerror("Scan error", str(error))

    def display_scan_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        total_files = sum(
            len(files) for files in self.scan_results.values()
        )

        ctk.CTkLabel(
            self.results_frame,
            text=f"Total files found: {total_files}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=10)

        if not self.scan_results:
            ctk.CTkLabel(
                self.results_frame,
                text="No files found in this folder."
            ).pack(anchor="w", padx=15, pady=10)
            return

        for category, files in sorted(self.scan_results.items()):
            card = ctk.CTkFrame(self.results_frame)
            card.pack(fill="x", padx=10, pady=6)

            ctk.CTkLabel(
                card,
                text=f"{category} — {len(files)} file(s)",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", padx=12, pady=10)

            names = "\n".join(
                f"• {file.name}" for file in files[:8]
            )

            if len(files) > 8:
                names += f"\n• ...and {len(files) - 8} more"

            ctk.CTkLabel(
                card,
                text=names,
                justify="left",
                anchor="w"
            ).pack(anchor="w", padx=12, pady=(0, 10))

    # ---------------- PREVIEW ----------------

    def preview_organization(self):
        if not self.selected_folder:
            messagebox.showwarning(
                "No folder selected",
                "Please select a folder first."
            )
            return

        try:
            self.preview_results = generate_preview(
                self.selected_folder
            )
            self.display_preview()

            total_files = sum(
                len(files) for files in self.preview_results.values()
            )

            self.status_label.configure(
                text=f"Preview ready: {total_files} file(s). Nothing moved."
            )

        except (OSError, ValueError) as error:
            messagebox.showerror("Preview error", str(error))

    def display_preview(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        total_files = sum(
            len(files) for files in self.preview_results.values()
        )

        ctk.CTkLabel(
            self.results_frame,
            text=f"Organization Preview — {total_files} file(s)",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=15, pady=10)

        if not self.preview_results:
            ctk.CTkLabel(
                self.results_frame,
                text="No files available to organize."
            ).pack(anchor="w", padx=15, pady=10)
            return

        for category, files in self.preview_results.items():
            card = ctk.CTkFrame(self.results_frame)
            card.pack(fill="x", padx=10, pady=6)

            ctk.CTkLabel(
                card,
                text=f"{category} — {len(files)} file(s)",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", padx=12, pady=8)

            for item in files[:5]:
                ctk.CTkLabel(
                    card,
                    text=f"{item['name']}  →  {category}/{item['name']}",
                    anchor="w",
                    wraplength=750
                ).pack(anchor="w", padx=12, pady=3)

            if len(files) > 5:
                ctk.CTkLabel(
                    card,
                    text=f"...and {len(files) - 5} more file(s)",
                    anchor="w"
                ).pack(anchor="w", padx=12, pady=5)

        ctk.CTkButton(
            self.results_frame,
            text="Confirm and Organize Files",
            height=42,
            command=self.confirm_preview
        ).pack(fill="x", padx=10, pady=15)

    # ---------------- CONFIRM AND ORGANIZE ----------------

    def confirm_preview(self):
        if not self.preview_results or not any(
            self.preview_results.values()
        ):
            messagebox.showinfo(
                "Nothing to organize",
                "Generate a preview containing files first."
            )
            return

        total_files = sum(
            len(files) for files in self.preview_results.values()
        )

        answer = messagebox.askyesno(
            "Confirm File Organization",
            f"Organize {total_files} file(s)?\n\n"
            f"Source folder:\n{self.selected_folder}\n\n"
            "Files will be moved into category folders inside "
            "the selected folder.\n\n"
            "Existing files will not be overwritten.\n\n"
            "This action moves files. There is no undo feature yet.\n\n"
            "Continue?"
        )

        if not answer:
            self.status_label.configure(
                text="Organization cancelled. No files were moved."
            )
            return

        try:
            report = organize_files(
                self.preview_results,
                self.selected_folder,
                confirm=True
            )

            moved = report["moved"]
            skipped = report["skipped"]
            errors = report["errors"]

            self.status_label.configure(
                text=(
                    f"Finished: {len(moved)} moved, "
                    f"{len(skipped)} skipped, "
                    f"{len(errors)} errors."
                )
            )

            summary = (
                "Organization finished!\n\n"
                f"Moved: {len(moved)}\n"
                f"Skipped: {len(skipped)}\n"
                f"Errors: {len(errors)}"
            )

            details = moved + skipped + errors

            if details:
                summary += "\n\nDetails:\n"
                summary += "\n".join(details[:15])

                if len(details) > 15:
                    summary += (
                        f"\n...and {len(details) - 15} more entries."
                    )

            if errors:
                messagebox.showwarning(
                    "Organization Report", summary
                )
            else:
                messagebox.showinfo(
                    "Organization Report", summary
                )

            # Refresh the scan after moving files.
            self.scan_results = scan_folder(self.selected_folder)
            self.preview_results = {}
            self.display_scan_results()

        except (OSError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror(
                "Organization error",
                f"An error occurred:\n{error}"
            )


if __name__ == "__main__":
    app = FileClassifierApp()
    app.mainloop()
