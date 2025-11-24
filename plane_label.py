# plane_label.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

app = QApplication(sys.argv)

img = QLabel()
# si plane.png est ailleurs, mets le chemin complet : Path("img/plane.png")
img_path = Path(__file__).with_name("plane.png")
img.setPixmap(QPixmap(str(img_path)))
img.setScaledContents(True)       # l’image s’adapte
img.resize(300, 200)
img.setAlignment(Qt.AlignCenter)
img.show()

sys.exit(app.exec())
