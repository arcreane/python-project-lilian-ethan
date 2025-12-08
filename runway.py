# piste d'atterissage
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QPixmap


class RunwayItem(QGraphicsPixmapItem):
    def __init__(self, scale: float = 0.5, parent=None):
        pix = QPixmap(":/img/runway.png")
        if pix.isNull():
            raise RuntimeError("Image :/img/runway.png introuvable dans resources.qrc")

        super().__init__(pix, parent)

        # Centre de la piste
        # on centre la pixmap
        self.setOffset(-pix.width() / 2, -pix.height() / 2)

        # Les transformations (scale, rotation) se font autour de (0, 0)
        self.setTransformOriginPoint(0, 120)

        # Taille de la piste
        self.setScale(scale)

        # Niveau d'affichage
        self.setZValue(0.5)
