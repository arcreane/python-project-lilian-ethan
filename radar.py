# radar.py
import math
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtGui import QPen, QBrush, QFont, QColor
from PySide6.QtCore import Qt

class RadarDrawer:

    def __init__(self, scene):
        self.scene = scene

    def draw(self, cx, cy, R):
        bg = QGraphicsEllipseItem(cx - R, cy - R, 2*R, 2*R)
        bg.setPen(QPen(Qt.white, 1))
        bg.setBrush(QBrush(Qt.black))
        self.scene.addItem(bg)

        # cercles
        for k in range(1, 6):
            r = R * k / 4
            c = QGraphicsEllipseItem(cx - r, cy - r, 2*r, 2*r)
            c.setPen(QPen(Qt.darkGray, 1, Qt.DashLine))
            self.scene.addItem(c)

        # axes
        axis_pen = QPen(Qt.gray, 1)
        self.scene.addLine(cx - R, cy, cx + R, cy, axis_pen)
        self.scene.addLine(cx, cy - R, cx, cy + R, axis_pen)

        # ticks + labels
        tick_pen = QPen(Qt.lightGray, 1)
        font = QFont("Segoe UI", 9)
        for deg in range(0, 360, 10):
            rad = math.radians(deg)
            major = (deg % 30 == 0)
            tlen = 14 if major else 7
            x1 = cx + (R - tlen) * math.cos(rad)
            y1 = cy + (R - tlen) * math.sin(rad)
            x2 = cx + R * math.cos(rad)
            y2 = cy + R * math.sin(rad)
            self.scene.addLine(x1, y1, x2, y2, tick_pen)

            if major:
                tx = cx + (R + 18) * math.cos(rad)
                ty = cy + (R + 18) * math.sin(rad)
                label = QGraphicsTextItem(str(deg))
                label.setDefaultTextColor(Qt.white)
                label.setFont(font)
                br = label.boundingRect()
                label.setPos(tx - br.width()/2, ty - br.height()/2)
                self.scene.addItem(label)

