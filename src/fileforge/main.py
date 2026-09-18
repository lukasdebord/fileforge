import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

app = QApplication(sys.argv)

window = QMainWindow()
label = QLabel("hello world")
window.setCentralWidget(label)

window.show()

app.exec()
