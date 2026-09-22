"""
    drop_zone.py -> contains the DropZone class for the FileForge application.

    Last updated: 9/21/26
    Contributor: Lukas DeBord
"""

# imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame


class DropZone(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # set the object name for styling purposes
        self.setObjectName("dropZone")
        # allow the drop zone to accept drops
        self.setAcceptDrops(True)

