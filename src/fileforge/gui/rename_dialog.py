"""
    rename-dialog.py -> consists of the rename dialog window for the FileForge application.
    It contains the UI elements for renaming files.

    Last updated: 10/28/26
    Contributor: Lukas DeBord
"""

# imports
from pathlib import Path

from PySide6.QtCore import (
    QSettings
)

from PySide6.QtWidgets import (
    QDialog,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

# ==================================================
# INITIALIZATION
# ==================================================
class RenameDialog(QDialog):
    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)

        # expand the user home directory and resolve the absolute path of the file
        self.file_path = Path(file_path).expanduser().resolve()

        self.setWindowTitle("Rename with FileForge")
        self.setMinimumWidth(360)

        self._build_ui()


# ==================================================
# UI SETUP
# ==================================================

    # --- UI CONSTRUCTION ---
    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._build_file_info_ui(layout)
        self._build_naming_options_ui(layout)
        self._build_extension_ui(layout)
        self._build_button_ui(layout)



    # -- File info UI ---
    def _build_file_info_ui(self, layout):
        layout.addWidget(QLabel("Original filename:"))

        # show the original filename without the extension
        self.original_file_name = QLabel(self.file_path.stem)

        layout.addWidget(self.original_file_name)


    # --- NAMING OPTIONS UI ---
    def _build_naming_options_ui(self, layout):
                # file renaming input
        rename_layout = QHBoxLayout()

        self.settings = QSettings("FileForge", "RenameDialog")

        self.file_name_prefix = QComboBox()
        self.file_name_prefix.setEditable(True)
        self.file_name_prefix.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # Define the default prefixes for the file name prefix combo box
        DEFAULT_PREFIXES = [
            "ITCS131",
            "ITCS132",
            "ITCS133",
        ]

        # Initialize the file name prefixes in the settings if they don't exist.
        if not self.settings.contains("file_name_prefixes"):
            self.settings.setValue(
                "file_name_prefixes", 
                DEFAULT_PREFIXES
            )

        # Retrieve the saved prefixes from the settings, falling back to the default prefixes 
        # if none are saved.
        saved_prefixes = self.settings.value(
            "file_name_prefixes",
            type = list
        )

        self.file_name_prefix.addItems(saved_prefixes)

        # add a button to add new file name prefixes
        self.add_file_name_prefix_btn = QPushButton("+")
        self.add_file_name_prefix_btn.clicked.connect(self.add_file_name_prefix)

        # add a button to add new file name prefixes
        self.delete_file_name_prefix_btn = QPushButton("-")
        self.delete_file_name_prefix_btn.clicked.connect(self.delete_file_name_prefix)


        rename_layout.addWidget(self.file_name_prefix)
        rename_layout.addWidget(self.add_file_name_prefix_btn)
        rename_layout.addWidget(self.delete_file_name_prefix_btn)
        layout.addLayout(rename_layout)


    # --- EXTENSION UI ---
    def _build_extension_ui(self, layout):
        extension = self.file_path.suffix
        if extension:
            layout.addWidget(QLabel(f"Extension: {extension}"))


    # --- BUTTON UI ---
    def _build_button_ui(self, layout):
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        rename_button = QPushButton("Rename")
        rename_button.setDefault(True)

        cancel_button.clicked.connect(self.reject)
        rename_button.clicked.connect(self.rename_file)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(rename_button)

        layout.addLayout(button_layout)


    # ==================================================
    # PREFIX SETTINGS ADDITION AND DELETION
    # ==================================================

    # --- ADD FILE NAME PREFIX ---
    def add_file_name_prefix(self):
        # get current text from the combo box
        prefix = self.file_name_prefix.currentText().strip()
        if prefix:
            # add prefix and save to settings
            self.file_name_prefix.addItem(prefix)
            self.settings.setValue(
                "file_name_prefixes",
                [self.file_name_prefix.itemText(i) for i in range(self.file_name_prefix.count())]
            )

    # --- DELETE FILE NAME PREFIX ---
    def delete_file_name_prefix(self):
        # get the current index of the selected prefix in the combo box
        current_index = self.file_name_prefix.currentIndex()
        if current_index >= 0:
            # delete prefix and remove from settings
            self.file_name_prefix.removeItem(current_index)
            self.settings.setValue(
                "file_name_prefixes",
                [self.file_name_prefix.itemText(i) for i in range(self.file_name_prefix.count())]
            )

    # ==================================================
    # RENAME FILE ACTION
    # ==================================================
    def rename_file(self):
        new_name = self.file_name_prefix.currentText().strip()

        # check if file name is empty
        if not new_name:
            QMessageBox.warning(
                self,
                "Invalid filename",
                "The filename cannot be empty.",
            )
            return

        # Prevent entering a invalid characters in filename.
        prohibited_chars = [":", "*", "?", '"', "<", ">", "|"]
        if any(char in new_name for char in prohibited_chars):
            QMessageBox.warning(
                self,
                "Invalid filename",
                "The filename contains prohibited characters.",
            )
            return

        # Prevent entering a path instead of just a filename.
        if "/" in new_name or "\\" in new_name:
            QMessageBox.warning(
                self,
                "Invalid filename",
                "Enter a filename, not a path.",
            )
            return

        # Keep the original extension.
        new_path = self.file_path.with_name(
            new_name + self.file_path.suffix
        )

        if new_path == self.file_path:
            self.accept()
            return

        # Check if the new file path already exists before attempting to rename.
        if new_path.exists():
            QMessageBox.warning(
                self,
                "File already exists",
                f"A file named '{new_path.name}' already exists.",
            )
            return

        # Attempt to rename the file and check for errors
        try:
            self.file_path.rename(new_path)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Rename failed",
                f"Could not rename the file:\n{error}",
            )
            return

        self.file_path = new_path
        self.accept()
