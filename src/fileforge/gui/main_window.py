"""
    main_window.py -> consists of the main window for the FileForge application. 
    It contains the menu bar and other UI elements.

    Last updated: 9/21/26
    Contributor: Lukas DeBord
"""

# imports
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

from .menu_bar import MenuBar
from .drop_zone import DropZone

# MainWindow class definition
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # window configuration
        self.setWindowTitle("FileForge")
        self.resize(800, 600)

        # define the menu bar
        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)

        # define drag and drop zone
        drop_zone = DropZone(self)
        self.setCentralWidget(drop_zone)

        # Quit button
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(lambda: QApplication.instance().exit())

        #self.setCentralWidget(quit_btn)
