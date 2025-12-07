import math
import random
import warnings

from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QPainter, QPixmap, QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QPushButton,
    QToolBar,
    QColorDialog,
)

# ----------------------------------------------------------
#  Utils fusionnés ici (option 2)
# ----------------------------------------------------------

def safe_disconnect(signal):
    """Déconnecte un signal sans lever d’exception."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        try:
            signal.disconnect()
        except (RuntimeError, TypeError):
            pass


def tint_pixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """Applique une teinte sur un QPixmap."""
    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.transparent)

    painter = QPainter(tinted)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)

    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), color)
    painter.end()

    return tinted


# ----------------------------------------------------------
#  Radar Item
# ----------------------------------------------------------

class RadarItem:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.angle = 0
        self.speed = random.uniform(0.5, 2.0)
        self.color = QColor(0, 255, 0)

    def update(self):
        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360

    def draw(self, painter: QPainter):
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        painter.drawEllipse(QRectF(self.pos.x() - 5, self.pos.y() - 5, 10, 10))
        painter.restore()


# ----------------------------------------------------------
#  Radar Widget
# ----------------------------------------------------------

class RadarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.items = [RadarItem(QPointF(random.randint(50, 350),
                                        random.randint(50, 350)))
                      for _ in range(10)]

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_radar)
        self.timer.start(30)

    def update_radar(self):
        for item in self.items:
            item.update()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        painter.setPen(QColor(0, 255, 0))
        center = QPointF(self.width() / 2, self.height() / 2)

        painter.drawEllipse(center, 150, 150)
        painter.drawEllipse(center, 100, 100)
        painter.drawEllipse(center, 50, 50)

        for item in self.items:
            item.draw(painter)


# ----------------------------------------------------------
#  Fenêtre principale
# ----------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Radar Simulation")
        self.resize(600, 600)

        self.radar_widget = RadarWidget()
        self.setCentralWidget(self.radar_widget)

        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)

        change_color_action = QAction("Couleur Radar", self)
        change_color_action.triggered.connect(self.change_item_color)
        toolbar.addAction(change_color_action)

    def change_item_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            for item in self.radar_widget.items:
                item.color = color
            self.radar_widget.update()
