"""
    menu_bar.py -> contains the MenuBar class for the FileForge application.

    Last updated: 9/21/26
    Contributor: Lukas DeBord
"""

# imports
from PySide6.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        # File menu
        file_menu = self.addMenu("File")
        file_menu.addAction("New File")
        file_menu.addAction("New Window")
        file_menu.addSeparator()
        file_menu.addAction("Open File")
        file_menu.addAction("Open Folder")
        file_menu.addAction("Open Recent")
        file_menu.addSeparator()
        file_menu.addAction("Save")
        file_menu.addAction("Save As")
        file_menu.addSeparator()
        file_menu.addAction("Close File")
        file_menu.addAction("Close Window")

        # Edit menu
        edit_menu = self.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")

        # View menu
        view_menu = self.addMenu("View")
        view_menu.addAction("Zoom In")
        view_menu.addAction("Zoom Out")
        view_menu.addAction("Reset Zoom")

        # Window menu
        window_menu = self.addMenu("Window")
        window_menu.addAction("Minimize")
        window_menu.addAction("Maximize")

        # Organize menu
        organize_menu = self.addMenu("Organize")
        organize_menu.addAction("Move Files")
        organize_menu.addAction("Rename Files")
        organize_menu.addAction("Sort Files")

        # Help menu
        help_menu = self.addMenu("Help")
        help_menu.addAction("Keyboard Shortcuts")
        help_menu.addSeparator()
        help_menu.addAction("Documentation")
        help_menu.addAction("Check for Updates")
        help_menu.addAction("Report a Bug")
        help_menu.addAction("About")
                                