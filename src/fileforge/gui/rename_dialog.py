"""
    rename-dialog.py -> consists of the rename dialog window for the FileForge application.
    It contains the UI elements for renaming files.

    Last updated: 10/30/26
    Contributor: Lukas DeBord
"""

# imports
from datetime import date
from pathlib import Path

from PySide6.QtCore import (
    QPoint,
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
    QFrame,
)

from .prefix_fields import (
    _PrefixDragHandle,
    _PrefixFieldRow,
    _PrefixFieldsArea,
)

_FIELD_GROUPS = ("Class", "Separator", "Date", "Document type", "Custom")
_SEPARATORS = (
    ("Underscore (_)", "_"),
    ("Hyphen (-)", "-"),
    ("Space", " "),
)
_DATE_FORMATS = (
    ("YYYY-MM-DD", "%Y-%m-%d"),
    ("YYYYMMDD", "%Y%m%d"),
    ("MM-DD-YYYY", "%m-%d-%Y"),
)


# ==================================================
# INITIALIZATION
# ==================================================
class RenameDialog(QDialog):
    def __init__(self, file_paths: list[Path], parent=None):
        super().__init__(parent)

        self.settings = QSettings("FileForge", "RenameDialog")
        self.prohibited_chars = [":", "*", "?", '"', "<", ">", "|", "/", "\\", ".", ","]

        # Initialize default filename prefixes if they don't exist in settings
        default_prefixes = ["ITCS131", "ITCS132", "ITCS133"]
        if not self.settings.contains("file_name_prefixes"):
            self.settings.setValue("file_name_prefixes", default_prefixes)

        self.saved_values = {
            "Class": self.settings.value(
                "file_name_prefixes",
                type=list,
            ) or [],
            "Document type": self.settings.value(
                "file_name_document_types",
                type=list,
            ) or [],
            "Custom": self.settings.value(
                "file_name_custom_values",
                type=list,
            ) or [],
        }

        self.prefix_fields = []
        self.prefix_groups = []
        self.prefix_field_rows = []
        self.drop_indicator = None

        # expand the user home directory and resolve the absolute path of the files
        self.file_paths = [
            Path(file_path).expanduser().resolve()
            for file_path in file_paths
        ]

        self.setWindowTitle("Rename with FileForge")
        self.setMinimumWidth(460)

        self._build_ui()


# ==================================================
# UI SETUP
# ==================================================

    # --- UI CONSTRUCTION ---
    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.prefix_fields_area = _PrefixFieldsArea(
            lambda: self.prefix_field_rows,
            self._move_prefix_row_by_id,
            self._show_drop_indicator,
            self._clear_drop_indicator,
        )
        self.prefix_fields_layout = QVBoxLayout(self.prefix_fields_area)
        self.prefix_fields_layout.setContentsMargins(0, 8, 0, 8)

        self._build_file_info_ui(layout)
        self._build_naming_field_ui(self.prefix_fields_layout)
        layout.addWidget(self.prefix_fields_area)
        # self._build_extension_ui(layout)
        self._build_button_ui(layout)



    # -- File info UI ---
    def _build_file_info_ui(self, layout):
        layout.addWidget(QLabel("Original filenames:"))

        # show the original filenames without the extension
        self.original_file_name = QLabel(
            "\n".join(
                str(file_path.name) for file_path in self.file_paths
            )
        )

        layout.addWidget(self.original_file_name)

        # add and delete buttons for filename components
        add_prefix_field = QPushButton("+")
        add_prefix_field.setFixedWidth(30)
        add_prefix_field.clicked.connect(self.add_file_name_prefix_field)


        prefix_layout_buttons = QHBoxLayout()

        # heading (preferably remove new line to use margin instead)
        prefix_layout_buttons.addWidget(QLabel("\nFilename components"))
        prefix_layout_buttons.addWidget(add_prefix_field)
        layout.addLayout(prefix_layout_buttons)


    # --- NAMING OPTIONS UI ---
    def _build_naming_field_ui(self, layout):
        # Create a row widget to hold the prefix field and its buttons
        row_widget = _PrefixFieldRow(self._drop_on_row, self._show_row_drop_indicator)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)

        # Initialize the prefix field row list if it doesn't exist
        group_field = QComboBox()
        group_field.addItems(_FIELD_GROUPS)
        group_field.setFixedWidth(110)

        field = QComboBox()
        group_field.currentTextChanged.connect(
            lambda group, value_field=field: self._configure_field(value_field, group)
        )
        self._configure_field(field, group_field.currentText())

        is_additional_field = bool(self.prefix_fields)
        if is_additional_field:
            field.setCurrentIndex(-1)
        self.prefix_fields.append(field)
        self.prefix_groups.append(group_field)

        # create a delete button for the prefix field
        delete_prefix_field = QPushButton("x")
        delete_prefix_field.setFixedWidth(30)
        delete_prefix_field.clicked.connect(
            lambda _checked=False, row=row_widget:
                self.delete_file_name_prefix_field(row)
        )

        # Add and delete buttons for this prefix field
        add_prefix_button = QPushButton("+")
        add_prefix_button.setFixedWidth(30)
        add_prefix_button.clicked.connect(
            lambda _checked=False, prefix_field=field, category=group_field:
                self.save_group_value(prefix_field, category)
        )

        delete_prefix_button = QPushButton("-")
        delete_prefix_button.setFixedWidth(30)
        delete_prefix_button.clicked.connect(
            lambda _checked=False, prefix_field=field, category=group_field:
                self.delete_group_value(prefix_field, category)
        )
        group_field.currentTextChanged.connect(
            lambda group, save_button=add_prefix_button, delete_button=delete_prefix_button:
                self._set_value_buttons_enabled(group, save_button, delete_button)
        )
        self._set_value_buttons_enabled(
            group_field.currentText(),
            add_prefix_button,
            delete_prefix_button,
        )

        drag_handle = _PrefixDragHandle(row_widget)
        drag_handle.clear_drop_indicator = self._clear_drop_indicator

        # Add the buttons to the row layout
        row_layout.addWidget(delete_prefix_field)
        row_layout.addWidget(group_field)
        row_layout.addWidget(field)
        row_layout.addWidget(add_prefix_button)
        row_layout.addWidget(delete_prefix_button)
        row_layout.addWidget(drag_handle)
        self.prefix_field_rows.append(row_widget)
        layout.addWidget(row_widget)


    # --- EXTENSION UI ---
    def _build_extension_ui(self, layout):
        extension = self.file_paths[0].suffix if self.file_paths else ""
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

    def _configure_field(self, field, group):
        field.blockSignals(True)
        field.clear()
        field.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        if group == "Separator":
            field.setEditable(False)
            for label, separator in _SEPARATORS:
                field.addItem(label, separator)
            field.setCurrentIndex(0)
        elif group == "Date":
            field.setEditable(False)
            for label, date_format in _DATE_FORMATS:
                field.addItem(label, date_format)
            field.setCurrentIndex(0)
        else:
            field.setEditable(True)
            field.addItems(self.saved_values.get(group, []))
            if field.count() == 0:
                field.setCurrentIndex(-1)

        field.blockSignals(False)

    @staticmethod
    def _set_value_buttons_enabled(group, save_button, delete_button):
        enabled = group in ("Class", "Document type", "Custom")
        save_button.setEnabled(enabled)
        delete_button.setEnabled(enabled)

    # --- ADD FILE NAME PREFIX FIELD ---
    def add_file_name_prefix_field(self):
        self._build_naming_field_ui(self.prefix_fields_layout)

    # --- DELETE FILE NAME PREFIX FIELD ---
    def delete_file_name_prefix_field(self, row):
        if len(self.prefix_field_rows) <= 0:
            return

        index = self.prefix_field_rows.index(row)
        self.prefix_field_rows.pop(index)
        self.prefix_fields.pop(index)
        self.prefix_groups.pop(index)
 
        self.prefix_fields_layout.removeWidget(row)
        row.deleteLater()
        self.adjustSize()
        QTimer.singleShot(0, self.adjustSize)


    # ==================================================
    # SAVED GROUP VALUE MANAGEMENT
    # ==================================================

    # --- SAVE GROUP VALUE ---
    def _settings_key_for_group(self, group):
        return {
            "Class": "file_name_prefixes",
            "Document type": "file_name_document_types",
            "Custom": "file_name_custom_values",
        }[group]

    def save_group_value(self, field, group_field):
        # Get the current text from the combo box.
        prefix = field.currentText().strip()
        group = group_field.currentText()

        # check if the prefix is empty
        if not prefix:
            QMessageBox.warning(
                self,
                "Invalid value",
                "The value cannot be empty.",
            )
            return

        # check if the prefix contains prohibited characters
        if any(char in prefix for char in self.prohibited_chars):
            QMessageBox.warning(
                self,
                "Invalid value",
                "The value contains prohibited characters.",
            )
            return

        # check for duplicate prefixes
        saved_values = self.saved_values[group]
        if prefix in saved_values:
            QMessageBox.warning(
                self,
                "Duplicate value",
                "This value is already saved.",
            )
            return

        saved_values.append(prefix)
        for prefix_field, prefix_group in zip(self.prefix_fields, self.prefix_groups):
            if prefix_group.currentText() == group:
                prefix_field.addItem(prefix)
        self.settings.setValue(self._settings_key_for_group(group), saved_values)

    # --- DELETE GROUP VALUE ---
    def delete_group_value(self, field, group_field):
        # Get the current index and text.
        current_index = field.currentIndex()
        current_text = field.currentText()
        group = group_field.currentText()

        # Only saved values can be removed from the list.
        if current_index < 0:
            return

        # Check if the current text is in the saved values list.
        saved_values = self.saved_values[group]
        if current_text not in saved_values:
            QMessageBox.warning(
                self,
                "Value not found",
                "This value is not saved.",
            )
            return

        saved_values.remove(current_text)
        for prefix_field, prefix_group in zip(self.prefix_fields, self.prefix_groups):
            if prefix_group.currentText() == group:
                prefix_field.removeItem(prefix_field.findText(current_text))
        self.settings.setValue(self._settings_key_for_group(group), saved_values)


    # ==================================================
    # DRAG FILE NAME PREFIX
    # ==================================================
    def _show_drop_indicator(self, insertion_index):
        """Show the insertion line at a slot before, between, or after the rows."""
        if self.drop_indicator is None:
            self.drop_indicator = QFrame(self.prefix_fields_area)
            self.drop_indicator.setFrameShape(QFrame.Shape.HLine)
            self.drop_indicator.setFrameShadow(QFrame.Shadow.Sunken)
            self.drop_indicator.setLineWidth(2)
            self.drop_indicator.setFixedHeight(4)

        rows = self.prefix_field_rows
        if not rows:
            return

        insertion_index = max(0, min(insertion_index, len(rows)))
        if insertion_index == 0:
            # Use the padded top margin so the marker does not sit under the first row.
            first_row_top = rows[0].mapTo(self.prefix_fields_area, QPoint(0, 0)).y()
            y_position = first_row_top // 2
        elif insertion_index == len(rows):
            last_row_bottom = (
                rows[-1].mapTo(self.prefix_fields_area, QPoint(0, 0)).y()
                + rows[-1].height()
            )
            y_position = (last_row_bottom + self.prefix_fields_area.height()) // 2
        else:
            previous_bottom = (
                rows[insertion_index - 1].mapTo(self.prefix_fields_area, QPoint(0, 0)).y()
                + rows[insertion_index - 1].height()
            )
            next_top = rows[insertion_index].mapTo(self.prefix_fields_area, QPoint(0, 0)).y()
            y_position = (previous_bottom + next_top) // 2

        self.drop_indicator.setGeometry(
            8,
            y_position - self.drop_indicator.height() // 2,
            max(0, self.prefix_fields_area.width() - 16),
            self.drop_indicator.height(),
        )
        self.drop_indicator.show()
        self.drop_indicator.raise_()

    def _show_row_drop_indicator(self, target_row, insertion_after):
        target_index = self.prefix_field_rows.index(target_row)
        self._show_drop_indicator(target_index + int(insertion_after))

    def _clear_drop_indicator(self):
        if self.drop_indicator is not None:
            self.drop_indicator.hide()

    def _drop_on_row(self, source_row_id, target_row, insertion_after):
        target_index = self.prefix_field_rows.index(target_row)
        self._move_prefix_row_by_id(source_row_id, target_index + int(insertion_after))

    def _move_prefix_row_by_id(self, source_row_id, insertion_index):
        self._clear_drop_indicator()
        source_row = next(
            (row for row in self.prefix_field_rows if id(row) == source_row_id),
            None,
        )
        if source_row is not None:
            self.move_prefix_row(source_row, insertion_index)

    def move_prefix_row(self, source_row, insertion_index):
        """Reorder the layout and its parallel lists to keep filename order in sync."""
        source_index = self.prefix_field_rows.index(source_row)
        insertion_index = max(0, min(insertion_index, len(self.prefix_field_rows)))
        # These two slots represent no movement: immediately before or after itself.
        if insertion_index in (source_index, source_index + 1):
            return

        row = self.prefix_field_rows.pop(source_index)
        field = self.prefix_fields.pop(source_index)
        group = self.prefix_groups.pop(source_index)

        if source_index < insertion_index:
            insertion_index -= 1

        self.prefix_field_rows.insert(insertion_index, row)
        self.prefix_fields.insert(insertion_index, field)
        self.prefix_groups.insert(insertion_index, group)

        self.prefix_fields_layout.removeWidget(row)
        self.prefix_fields_layout.insertWidget(insertion_index, row)

    # ==================================================
    # RENAME FILE ACTION
    # ==================================================
    def rename_file(self):
        name_parts = []
        pending_separator = ""
        for group_field, value_field in zip(self.prefix_groups, self.prefix_fields):
            group = group_field.currentText()
            if group == "Separator":
                if name_parts:
                    pending_separator = value_field.currentData()
                continue
            if group == "Date":
                value = date.today().strftime(value_field.currentData())
            else:
                value = value_field.currentText().strip()
            if value:
                if name_parts:
                    name_parts.append(pending_separator)
                name_parts.append(value)
                pending_separator = ""
        new_name = "".join(name_parts)

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

        # Keep each original extension and add a sequence number for batch renames.
        new_paths = [
            file_path.with_name(
                f"{new_name}{index if len(self.file_paths) > 1 else ''}"
                f"{file_path.suffix}"
            )
            for index, file_path in enumerate(self.file_paths, start=1)
        ]

        if all(
            new_path == file_path
            for file_path, new_path in zip(self.file_paths, new_paths)
        ):
            self.accept()
            return

        # Check every destination before renaming any file.
        conflicts = [
            new_path
            for file_path, new_path in zip(self.file_paths, new_paths)
            if new_path != file_path and new_path.exists()
        ]
        if conflicts:
            QMessageBox.warning(
                self,
                "File already exists",
                "A file already exists at:\n"
                + "\n".join(str(path) for path in conflicts),
            )
            return

        for index, (file_path, new_path) in enumerate(
            zip(self.file_paths, new_paths)
        ):
            if new_path == file_path:
                continue
            try:
                file_path.rename(new_path)
            except OSError as error:
                QMessageBox.critical(
                    self,
                    "Rename failed",
                    f"Could not rename '{file_path.name}':\n{error}",
                )
                return
            self.file_paths[index] = new_path

        self.accept()
