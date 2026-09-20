"""
    main_window.py -> entry point for the FileForge application
    run with python src/fileforge/main.py

    Last updated: 9/19/26
    Contributor: Lukas DeBord
"""

# imports

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton


# MainWindow class definition
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # window configuration
        self.setWindowTitle("FileForge")
        self.resize(800, 600)

        quit_btn = QPushButton("hello world")
        quit_btn.clicked.connect(lambda: QApplication.instance().exit())

        self.setCentralWidget(quit_btn)
