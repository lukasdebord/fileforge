"""
    This is the main entry point for the FileForge application. 
    It creates a QApplication instance, sets the style sheet, and displays the main window.

    Last updated: 9/21/26
    Contributor: Lukas DeBord
"""

# imports
import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from fileforge.gui.main_window import MainWindow
from fileforge.gui.rename_dialog import RenameDialog



# main function for the FileForge application
def main():
    # define parser and add arguments for command-line usage
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rename",
        type=Path,
        help="Open the rename dialog for a selected file",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # determine which window to display based on command-line arguments
    # args.rename contains the path to the file if the --rename argument was provided
        # this could be used later for implementing Open with FileForge functionality
    if args.rename:
        file_path = args.rename.expanduser().resolve()

        # file not found -> error out with a message
        if not file_path.is_file():
            parser.error(f"File not found: {file_path}")

        # create the rename dialog window for the selected file
        window = RenameDialog(file_path)
    # if no --rename argument was provided, display the main window
    else:
        window = MainWindow()

    window.show()
    sys.exit(app.exec())

# entry point for the script
if __name__ == "__main__":
    main()