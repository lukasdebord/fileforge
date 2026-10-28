"""
    main_window.py -> consists of the main window for the FileForge application. 
    It contains the menu bar and other UI elements.

    Last updated: 9/21/26
    Contributor: Lukas DeBord
"""

# imports
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

from fileforge.gui.menu_bar import MenuBar
from fileforge.gui.drop_zone import DropZone

# MainWindow class definition
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #================================================================================
        # === EXTERNAL WINDOW CONFIGURATION =============================================
        #================================================================================

        self.setWindowTitle("FileForge")
        self.resize(800, 600)

        # define the menu bar
        menu_bar = MenuBar(self)
        self.setMenuBar(menu_bar)



        # ================================================================================
        # === MAIN WINDOW CONFIGURATION ==================================================
        # ================================================================================

        # main window container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # main layout
        main_layout = QVBoxLayout(central_widget)

        # --------------------------------------------------------------------------------
        # --- Components -----------------------------------------------------------------
        # --------------------------------------------------------------------------------

        # file drop zone
        drop_zone = DropZone(self)

        # quit button
        quit_btn = QPushButton("Quit")
        quit_btn.clicked.connect(lambda: QApplication.instance().exit())

        # --------------------------------------------------------------------------------
        # --- Assembly -------------------------------------------------------------------
        # --------------------------------------------------------------------------------

        main_layout.addWidget(drop_zone)
        main_layout.addWidget(quit_btn)