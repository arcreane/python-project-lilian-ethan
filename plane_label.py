# plane_label.py

from pathlib import Path
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class PlaneLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Chargement de l'image plane.png dans le même dossier
        img_path = Path(__file__).with_name("plane.png")

        pix = QPixmap(str(img_path))
        self.setPixmap(pix)

        self.setScaledContents(True)
        self.resize(50, 100)
        self.setAlignment(Qt.AlignCenter)
