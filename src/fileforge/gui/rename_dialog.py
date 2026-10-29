"""
    rename-dialog.py -> consists of the rename dialog window for the FileForge application.
    It contains the UI elements for renaming files.

    Last updated: 10/28/26
    Contributor: Lukas DeBord
"""

# imports
from pathlib import Path

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

# class definition for the rename dialog window
# uses QDialog from PySide6.QtWidgets
class RenameDialog(QDialog):
    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)

        # expand the user home directory and resolve the absolute path of the file
        self.file_path = Path(file_path).expanduser().resolve()

        self.setWindowTitle("Rename with FileForge")
        self.setMinimumWidth(360)

        self._build_ui()



# build the user interface for the rename dialog window
    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("New filename:"))

        self.name_input = QLineEdit()
        
        # show original filename without the extension
        self.name_input.setText(self.file_path.stem)
        self.name_input.selectAll()

        layout.addWidget(self.name_input)

        # Show the extension separately so it stays unchanged.
        extension = self.file_path.suffix
        if extension:
            layout.addWidget(QLabel(f"Extension: {extension}"))

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


# handle the renaming of the file when the rename button is clicked
    def rename_file(self):
        new_name = self.name_input.text().strip()

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
