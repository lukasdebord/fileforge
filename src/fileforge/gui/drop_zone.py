"""
    drop_zone.py -> contains the DropZone class for the FileForge application.

    Last updated: 9/21/26
    Contributor: Lukas DeBord
"""

# imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout


class DropZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # set the object name for styling purposes
        self.setObjectName("dropZone")
        # allow the drop zone to accept drops
        self.setAcceptDrops(True)

        # drag and drop files label
        drop_zone_label = QLabel("Drag and Drop\nor")
        drop_zone_label.setAlignment(Qt.AlignCenter)
        drop_zone_label.setObjectName("dropZoneLabel")

        # import files button
        import_files_button = QPushButton("Browse Files")
        import_files_button.setObjectName("importFilesButton")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(drop_zone_label)
        self.layout().addWidget(import_files_button)
