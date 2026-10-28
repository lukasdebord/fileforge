"""
    This is the main entry point for the FileForge application. 
    It creates a QApplication instance, sets the style sheet, and displays the main window.

    Last updated: 9/21/26
    Contributor: Lukas DeBord
"""

# imports
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from fileforge.gui.main_window import MainWindow

# main function
if __name__ == "__main__":
    # create the application instance
    app = QApplication(sys.argv)

    # set the style sheets for the application
    style_sheet_path = Path(__file__).parent / "gui" / "stylesheets"

    style_sheet = ""

    # read all .qss files in the stylesheets directory and concatenate them
    for file in style_sheet_path.glob("*.qss"):
        style_sheet += file.read_text() + "\n"

    app.setStyleSheet(style_sheet)

    # display the main window
    window = MainWindow()

    window.show()
    app.exec()
