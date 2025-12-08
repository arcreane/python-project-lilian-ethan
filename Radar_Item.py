from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt
import math

class RadarItem:
    def __init__(self, scene, cx, cy, R):
        self.scene = scene
        self.cx = cx
        self.cy = cy
        self.R = R
        self.items = []  # tous les items du radar

        self.draw()

    def clear(self):
        for item in self.items:
            self.scene.removeItem(item)
        self.items.clear()

    def draw(self):
        self.clear()

        # Cercle principal
        bg = QGraphicsEllipseItem(self.cx - self.R, self.cy - self.R, 2*self.R, 2*self.R)
        bg.setPen(QPen(Qt.white, 2))
        bg.setBrush(QBrush(Qt.black))
        self.scene.addItem(bg)
        self.items.append(bg)

        # Cercles internes
        for k in range(1, 4):
            r = self.R * k / 4
            c = QGraphicsEllipseItem(self.cx - r, self.cy - r, 2*r, 2*r)
            c.setPen(QPen(Qt.darkGray, 1, Qt.DashLine))
            self.scene.addItem(c)
            self.items.append(c)

        # Axes
        axis_pen = QPen(Qt.gray, 1)
        x1 = self.scene.addLine(self.cx - self.R, self.cy, self.cx + self.R, self.cy, axis_pen)
        y1 = self.scene.addLine(self.cx, self.cy - self.R, self.cx, self.cy + self.R, axis_pen)
        self.items += [x1, y1]

        # Graduations
        tick_pen = QPen(Qt.lightGray, 1)
        font = QFont("Segoe UI", 9)

        for deg in range(0, 360, 10):
            rad = math.radians(deg)
            is_major = (deg % 30 == 0)
            tlen = 14 if is_major else 7

            x1 = self.cx + (self.R - tlen) * math.cos(rad)
            y1 = self.cy + (self.R - tlen) * math.sin(rad)
            x2 = self.cx + self.R * math.cos(rad)
            y2 = self.cy + self.R * math.sin(rad)
            tick = self.scene.addLine(x1, y1, x2, y2, tick_pen)
            self.items.append(tick)

            if is_major:
                tx = self.cx + (self.R + 18) * math.cos(rad)
                ty = self.cy + (self.R + 18) * math.sin(rad)
                label = QGraphicsTextItem(str(deg))
                label.setDefaultTextColor(Qt.white)
                label.setFont(font)
                br = label.boundingRect()
                label.setPos(tx - br.width()/2, ty - br.height()/2)
                self.scene.addItem(label)
                self.items.append(label)

    def reposition(self, cx, cy, R):
        self.cx = cx
        self.cy = cy
        self.R = R
        self.draw()
