# app.py
import sys
from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec())
