# app.py — Radar circulaire + degrés + plusieurs avions
import sys, math, random
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem
)
from PySide6.QtGui import QPixmap, QPen, QBrush, QFont
from PySide6.QtCore import QTimer, QElapsedTimer, Qt, Slot

from ui_demo import Ui_MainWindow      # généré depuis demo.ui
import resources_rc                    # pour :/img/plane.png


@dataclass
class PlaneState:
    x: float
    y: float
    heading_deg: float   # cap (0°=droite, 90°=bas)
    speed: float         # px/s


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # récupérer la vue dans l'UI (radarView OU graphicsView)
        self.view: QGraphicsView | None = getattr(self.ui, "radarView", None) or getattr(self.ui, "graphicsView", None)
        if self.view is None:
            raise RuntimeError("Aucune QGraphicsView trouvée ('radarView' ou 'graphicsView').")

        # scène
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # taille de la scène
        self.W, self.H = 800, 600
        self.scene.setSceneRect(0, 0, self.W, self.H)

        # centre et rayon du radar
        self.cx, self.cy = self.W / 2, self.H / 2
        self.R = min(self.W, self.H) * 0.42  # marge

        # 1) dessiner le radar
        self.draw_radar()

        # 2) créer plusieurs avions
        self.planes: list[QGraphicsPixmapItem] = []
        self.states: list[PlaneState] = []
        self.make_planes(n=5)  # <<< nombre d'avions au départ

        # 3) timer simu
        self.clock = QElapsedTimer()
        self.clock.start()

        self.timer = QTimer(self)
        self.timer.setInterval(50)  # 20 Hz
        self.timer.timeout.connect(self.tick)
        self.timer.start()

    # ---------- RADAR ----------
    def draw_radar(self):
        # cercle principal
        bg = QGraphicsEllipseItem(self.cx - self.R, self.cy - self.R, 2*self.R, 2*self.R)
        bg.setPen(QPen(Qt.white, 2))
        bg.setBrush(QBrush(Qt.black))
        self.scene.addItem(bg)

        # cercles internes (effet radar)
        for k in range(1, 4):
            r = self.R * k / 4
            c = QGraphicsEllipseItem(self.cx - r, self.cy - r, 2*r, 2*r)
            c.setPen(QPen(Qt.darkGray, 1, Qt.DashLine))
            self.scene.addItem(c)

        # axes X/Y
        axis_pen = QPen(Qt.gray, 1)
        self.scene.addLine(self.cx - self.R, self.cy, self.cx + self.R, self.cy, axis_pen)
        self.scene.addLine(self.cx, self.cy - self.R, self.cx, self.cy + self.R, axis_pen)

        # ticks + labels degrés
        tick_pen = QPen(Qt.lightGray, 1)
        font = QFont("Segoe UI", 9)

        for deg in range(0, 360, 10):  # tick tous les 10°
            rad = math.radians(deg)
            is_major = (deg % 30 == 0)
            tlen = 14 if is_major else 7

            x1 = self.cx + (self.R - tlen) * math.cos(rad)
            y1 = self.cy + (self.R - tlen) * math.sin(rad)
            x2 = self.cx + self.R * math.cos(rad)
            y2 = self.cy + self.R * math.sin(rad)
            self.scene.addLine(x1, y1, x2, y2, tick_pen)

            if is_major:
                tx = self.cx + (self.R + 18) * math.cos(rad)
                ty = self.cy + (self.R + 18) * math.sin(rad)
                label = QGraphicsTextItem(str(deg))
                label.setDefaultTextColor(Qt.white)
                label.setFont(font)
                br = label.boundingRect()
                label.setPos(tx - br.width()/2, ty - br.height()/2)
                self.scene.addItem(label)

    # ---------- AVIONS ----------
    def make_planes(self, n=5):
        for _ in range(n):
            self.add_one_plane()

    def add_one_plane(self):
        pix = QPixmap(":/img/plane.png")
        if pix.isNull():
            raise RuntimeError("Image :/img/plane.png introuvable dans resources.qrc")

        item = QGraphicsPixmapItem(pix)
        item.setScale(0.35)  # taille avion
        item.setTransformOriginPoint(item.boundingRect().center())
        self.scene.addItem(item)

        # position aléatoire dans le cercle
        angle = random.uniform(0, 2*math.pi)
        radius = random.uniform(0, self.R * 0.8)
        x = self.cx + radius * math.cos(angle)
        y = self.cy + radius * math.sin(angle)

        heading = random.uniform(0, 360)
        speed = random.uniform(80, 180)

        self.planes.append(item)
        self.states.append(PlaneState(x=x, y=y, heading_deg=heading, speed=speed))

    # ---------- SIMULATION ----------
    def tick(self):
        dt = self.clock.elapsed() / 1000.0
        self.clock.restart()
        if dt <= 0:
            return

        for item, st in zip(self.planes, self.states):
            # avancer selon cap
            rad = math.radians(st.heading_deg)
            nx = st.x + st.speed * math.cos(rad) * dt
            ny = st.y + st.speed * math.sin(rad) * dt

            # distance au centre
            dx = nx - self.cx
            dy = ny - self.cy
            dist = math.hypot(dx, dy)

            # rebond si sortie du radar
            if dist >= self.R:
                # normal au bord
                nx_norm = dx / dist if dist != 0 else 1
                ny_norm = dy / dist if dist != 0 else 0

                # vitesse direction actuelle (unitaire)
                vx = math.cos(rad)
                vy = math.sin(rad)

                # réflexion : v' = v - 2*(v·n)*n
                dot = vx * nx_norm + vy * ny_norm
                rvx = vx - 2 * dot * nx_norm
                rvy = vy - 2 * dot * ny_norm

                st.heading_deg = (math.degrees(math.atan2(rvy, rvx))) % 360

                # replacer juste à l’intérieur
                nx = self.cx + (self.R - 1) * nx_norm
                ny = self.cy + (self.R - 1) * ny_norm

            st.x, st.y = nx, ny

            # centrer l’avion sur sa position
            b = item.boundingRect()
            item.setPos(st.x - b.width()/2, st.y - b.height()/2)
            item.setRotation(st.heading_deg)

    # ---------- SLOT BOUTON ----------
    @Slot()
    def demo(self):
        # appelé par pushButton.clicked si tu as gardé la connexion dans Designer
        self.add_one_plane()
        self.statusBar().showMessage("Nouvel avion ajouté", 1200)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
