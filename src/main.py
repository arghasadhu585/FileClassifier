
from pathlib import Path
from .scanner.folder_scanner import scan_folder
from .gui.preview_screen import generate_preview, print_preview


def main():
    print("=" * 45)
    print("         FILECLASSIFIER")
    print("     Smart File Organization Tool")
    print("=" * 45)

    while True:
        print("\n1. Scan a folder")
        print("2. Preview file organization")
        print("3. Exit")

        choice = input("\nChoose an option (1-3): ").strip()

        if choice == "1":
            folder_path = input("Enter folder path: ").strip().strip('"')

            try:
                results = scan_folder(folder_path)

                print("\n--- Scan Results ---")
                total_files = 0

                for category, files in sorted(results.items()):
                    print(f"\n{category}: {len(files)} file(s)")
                    total_files += len(files)

                print(f"\nTotal files found: {total_files}")

            except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
                print(f"Error: {error}")

        elif choice == "2":
            folder_path = input("Enter folder path: ").strip().strip('"')

            try:
                preview = generate_preview(folder_path)
                print_preview(preview)

            except (FileNotFoundError, NotADirectoryError, PermissionError) as error:
                print(f"Error: {error}")

        elif choice == "3":
            print("Thank you for using FileClassifier!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
