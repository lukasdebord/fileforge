"""
    rename-dialog.py -> consists of the rename dialog window for the FileForge application.
    It contains the UI elements for renaming files.

    Last updated: 10/28/26
    Contributor: Lukas DeBord
"""

# imports
from pathlib import Path

from PySide6.QtCore import (
    QSettings,
    QTimer
)

from PySide6.QtWidgets import (
    QDialog,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QWidget,
)

# ==================================================
# INITIALIZATION
# ==================================================
class RenameDialog(QDialog):
    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)

        self.settings = QSettings("FileForge", "RenameDialog")
        self.prohibited_chars = [":", "*", "?", '"', "<", ">", "|", "/", "\\", ".", ","]

        # Initialize default filename prefixes if they don't exist in settings
        default_prefixes = ["ITCS131", "ITCS132", "ITCS133"]
        if not self.settings.contains("file_name_prefixes"):
            self.settings.setValue("file_name_prefixes", default_prefixes)

        self.saved_prefixes = self.settings.value(
            "file_name_prefixes",
            type=list,
        ) or []

        self.prefix_fields = []
        self.prefix_field_rows = []

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
        self.prefix_fields_layout = QVBoxLayout()

        self._build_file_info_ui(layout)
        self._build_naming_field_ui(self.prefix_fields_layout)
        layout.addLayout(self.prefix_fields_layout)
        self._build_extension_ui(layout)
        self._build_button_ui(layout)



    # -- File info UI ---
    def _build_file_info_ui(self, layout):
        layout.addWidget(QLabel("Original filename:"))

        # show the original filename without the extension
        self.original_file_name = QLabel(self.file_path.stem)

        layout.addWidget(self.original_file_name)

        # add and delete buttons for filename prefix fields
        add_prefix_field = QPushButton("+")
        add_prefix_field.setFixedWidth(30)
        add_prefix_field.clicked.connect(self.add_file_name_prefix_field)

        prefix_layout_buttons = QHBoxLayout()

        # heading (preferably remove new line to use margin instead)
        prefix_layout_buttons.addWidget(QLabel("\nFilename prefixes"))
        prefix_layout_buttons.addWidget(add_prefix_field)

        layout.addLayout(prefix_layout_buttons)


    # --- NAMING OPTIONS UI ---
    def _build_naming_field_ui(self, layout):
        # Create a row widget to hold the prefix field and its buttons
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        # Initialize the prefix field row list if it doesn't exist
        is_additional_field = bool(self.prefix_fields)
        field = QComboBox()
        field.setEditable(True)
        field.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        field.addItems(self.saved_prefixes)
        if is_additional_field:
            field.setCurrentIndex(-1)
        self.prefix_fields.append(field)

        # create a delete button for the prefix field
        delete_prefix_field = QPushButton("x")
        delete_prefix_field.setFixedWidth(30)
        delete_prefix_field.clicked.connect(
            lambda _checked=False, row=row_widget, prefix_field=field: 
                self.delete_file_name_prefix_field(row, prefix_field))

        # Add and delete buttons for this prefix field
        add_prefix_button = QPushButton("+")
        add_prefix_button.setFixedWidth(30)
        add_prefix_button.clicked.connect(
            lambda _checked=False, prefix_field=field: self.add_file_name_prefix(prefix_field)
        )

        delete_prefix_button = QPushButton("-")
        delete_prefix_button.setFixedWidth(30)
        delete_prefix_button.clicked.connect(
            lambda _checked=False, prefix_field=field: self.delete_file_name_prefix(prefix_field)
        )

        # Add the buttons to the row layout
        row_layout.addWidget(delete_prefix_field)
        row_layout.addWidget(field)
        row_layout.addWidget(add_prefix_button)
        row_layout.addWidget(delete_prefix_button)
        self.prefix_field_rows.append(row_widget)
        layout.addWidget(row_widget)


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
    # PREFIX FIELD ADDITION AND DELETION
    # ==================================================

    # --- ADD FILE NAME PREFIX FIELD ---
    def add_file_name_prefix_field(self):
        self._build_naming_field_ui(self.prefix_fields_layout)

    # --- DELETE FILE NAME PREFIX FIELD ---
    def delete_file_name_prefix_field(self, row, prefix_field):
        if len(self.prefix_field_rows) <= 0:
            return

        index = self.prefix_field_rows.index(row)
        self.prefix_field_rows.pop(index)
        self.prefix_fields.pop(index)
 
        self.prefix_fields_layout.removeWidget(row)
        row.deleteLater()
        self.adjustSize()
        QTimer.singleShot(0, self.adjustSize)


    # ==================================================
    # PREFIX SETTINGS ADDITION AND DELETION
    # ==================================================

    # --- ADD FILE NAME PREFIX ---
    def add_file_name_prefix(self, field):
        # get current text from the combo box
        prefix = field.currentText().strip()

        # check if the prefix is empty
        if not prefix:
            QMessageBox.warning(
                self,
                "Invalid prefix",
                "The prefix cannot be empty.",
            )
            return

        # check if the prefix contains prohibited characters
        if any(char in prefix for char in self.prohibited_chars):
            QMessageBox.warning(
                self,
                "Invalid prefix",
                "The prefix cannot contain prohibited characters.",
            )
            return

        # check for duplicate prefixes
        if prefix in self.saved_prefixes:
            QMessageBox.warning(
                self,
                "Duplicate prefix",
                "This prefix already exists.",
            )
            return

        self.saved_prefixes.append(prefix)
        for prefix_field in self.prefix_fields:
            prefix_field.addItem(prefix)
        self.settings.setValue("file_name_prefixes", self.saved_prefixes)

    # --- DELETE FILE NAME PREFIX ---
    def delete_file_name_prefix(self, field):
        # Get the current index and text.
        current_index = field.currentIndex()
        current_text = field.currentText()

        # Check that the selected prefix is saved.
        if current_index < 0:
            return

        # Check if the current text is in the saved prefixes list.
        if current_text not in self.saved_prefixes:
            QMessageBox.warning(
                self,
                "Prefix not found",
                "This prefix is not saved.",
            )
            return

        self.saved_prefixes.remove(current_text)
        for prefix_field in self.prefix_fields:
            prefix_field.removeItem(prefix_field.findText(current_text))
        self.settings.setValue("file_name_prefixes", self.saved_prefixes)

    # ==================================================
    # RENAME FILE ACTION
    # ==================================================
    def rename_file(self):
        prefixes = [
            field.currentText().strip()
            for field in self.prefix_fields
            if field.currentText().strip()
        ]
        new_name = "_".join(prefixes)

        # check if file name is empty
        if not new_name:
            QMessageBox.warning(
                self,
                "Invalid filename",
                "The filename cannot be empty.",
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

        # Prevent entering a invalid characters in filename.
        if any(char in new_name for char in self.prohibited_chars):
            QMessageBox.warning(
                self,
                "Invalid filename",
                "The filename contains prohibited characters.",
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
