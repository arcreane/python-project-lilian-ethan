# plane.py

import math
import random
from dataclasses import dataclass

from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtCore import Qt

from utils import tint_pixmap   # <-- ici, tout simple


ALT_COLORS = {
    1: QColor(0, 220, 0),
    2: QColor(0, 120, 255),
    3: QColor(220, 0, 0),
}


@dataclass
class PlaneState:
    x: float
    y: float
    heading_deg: float
    speed: float
    altitude: int


class PlaneItem(QGraphicsPixmapItem):
    def __init__(self, cx, cy, R):
        base_pix = QPixmap(":/img/plane.png")
        if base_pix.isNull():
            raise RuntimeError("Image :/img/plane.png introuvable")

        alt = random.choice([1, 2, 3])
        pix = tint_pixmap(base_pix, ALT_COLORS[alt])

        super().__init__(pix)

        self.setScale(0.05)
        self.setTransformOriginPoint(self.boundingRect().center())
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(Qt.LeftButton)

        # position aléatoire dans le cercle
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, R * 0.8)

        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)

        heading = random.uniform(0, 360)
        speed = random.uniform(70, 150)

        self.state = PlaneState(x=x, y=y, heading_deg=heading, speed=speed, altitude=alt)

        b = self.boundingRect()
        self.setPos(x - b.width() / 2, y - b.height() / 2)
        self.setRotation(heading)

    def recolor(self):
        base_pix = QPixmap(":/img/plane.png")
        pix = tint_pixmap(base_pix, ALT_COLORS[self.state.altitude])
        self.setPixmap(pix)
