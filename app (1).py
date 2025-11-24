# app.py — Radar circulaire + degrés + altitudes (couleur avion) + collisions + boutons altitude
import sys, math, random
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem
)
from PySide6.QtGui import QPixmap, QPen, QBrush, QFont, QColor, QPainter
from PySide6.QtCore import QTimer, QElapsedTimer, Qt, Slot

from ui_demo import Ui_MainWindow
import resources_rc  # pour :/img/plane.png


# Couleurs des niveaux d'altitude
ALT_COLORS = {
    1: QColor(0, 220, 0),     # vert
    2: QColor(0, 120, 255),   # bleu
    3: QColor(220, 0, 0),     # rouge
}


def tint_pixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """Retourne une copie du pixmap teintée."""
    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.transparent)

    painter = QPainter(tinted)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)

    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted.rect(), color)

    painter.end()
    return tinted


@dataclass
class PlaneState:
    x: float
    y: float
    heading_deg: float
    speed: float
    altitude: int   # 1,2,3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 1) récupérer la vue dans l'UI (radarView OU graphicsView)
        self.view: QGraphicsView | None = getattr(self.ui, "radarView", None) or getattr(self.ui, "graphicsView", None)
        if self.view is None:
            raise RuntimeError("Aucune QGraphicsView trouvée ('radarView' ou 'graphicsView').")

        # 2) scène
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.W, self.H = 800, 600
        self.scene.setSceneRect(0, 0, self.W, self.H)

        self.cx, self.cy = self.W / 2, self.H / 2
        self.R = min(self.W, self.H) * 0.42

        # 3) radar
        self.draw_radar()

        # 4) avions
        self.planes: list[QGraphicsPixmapItem] = []
        self.states: list[PlaneState] = []
        self.make_planes(n=6)

        # sélection
        self.selected_index = None

        # collisions (avec scale=0.05, 12–25 est pas mal)
        self.collision_dist = 18.0

        # 5) connecter boutons altitude (doivent exister dans demo.ui)
        if hasattr(self.ui, "btnUp"):
            self.ui.btnUp.clicked.connect(self.altitude_up)
        if hasattr(self.ui, "btnDown"):
            self.ui.btnDown.clicked.connect(self.altitude_down)

        # si tu as encore pushButton -> demo() dans Designer, ça évite l’erreur
        # (sinon, ça ne fait rien)
        # rien à connecter ici car ui_demo.py fait déjà la connexion

        # 6) timer simu
        self.clock = QElapsedTimer()
        self.clock.start()

        self.timer = QTimer(self)
        self.timer.setInterval(50)  # 20 Hz
        self.timer.timeout.connect(self.tick)
        self.timer.start()

    # ---------- RADAR ----------
    def draw_radar(self):
        bg = QGraphicsEllipseItem(self.cx - self.R, self.cy - self.R, 2 * self.R, 2 * self.R)
        bg.setPen(QPen(Qt.white, 2))
        bg.setBrush(QBrush(Qt.black))
        self.scene.addItem(bg)

        for k in range(1, 4):
            r = self.R * k / 4
            c = QGraphicsEllipseItem(self.cx - r, self.cy - r, 2 * r, 2 * r)
            c.setPen(QPen(Qt.darkGray, 1, Qt.DashLine))
            self.scene.addItem(c)

        axis_pen = QPen(Qt.gray, 1)
        self.scene.addLine(self.cx - self.R, self.cy, self.cx + self.R, self.cy, axis_pen)
        self.scene.addLine(self.cx, self.cy - self.R, self.cx, self.cy + self.R, axis_pen)

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
            self.scene.addLine(x1, y1, x2, y2, tick_pen)

            if is_major:
                tx = self.cx + (self.R + 18) * math.cos(rad)
                ty = self.cy + (self.R + 18) * math.sin(rad)
                label = QGraphicsTextItem(str(deg))
                label.setDefaultTextColor(Qt.white)
                label.setFont(font)
                br = label.boundingRect()
                label.setPos(tx - br.width() / 2, ty - br.height() / 2)
                self.scene.addItem(label)

    # ---------- AVIONS ----------
    def make_planes(self, n=5):
        for _ in range(n):
            self.add_one_plane()

    def recolor_plane(self, idx: int):
        """Re-teinte l'avion selon son altitude."""
        st = self.states[idx]
        base_pix = QPixmap(":/img/plane.png")
        tinted = tint_pixmap(base_pix, ALT_COLORS[st.altitude])
        self.planes[idx].setPixmap(tinted)

    def add_one_plane(self):
        base_pix = QPixmap(":/img/plane.png")
        if base_pix.isNull():
            raise RuntimeError("Image :/img/plane.png introuvable dans resources.qrc")

        # altitude aléatoire
        alt = random.choice([1, 2, 3])
        tinted_pix = tint_pixmap(base_pix, ALT_COLORS[alt])

        item = QGraphicsPixmapItem(tinted_pix)
        item.setScale(0.05)  # <<< taille demandée
        item.setTransformOriginPoint(item.boundingRect().center())
        self.scene.addItem(item)

        # rendre sélectionnable par clic
        item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        item.setAcceptedMouseButtons(Qt.LeftButton)

        # position aléatoire dans le cercle
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.R * 0.8)
        x = self.cx + radius * math.cos(angle)
        y = self.cy + radius * math.sin(angle)

        heading = random.uniform(0, 360)
        speed = random.uniform(70, 150)

        self.planes.append(item)
        self.states.append(PlaneState(x=x, y=y, heading_deg=heading, speed=speed, altitude=alt))

    # ---------- SELECTION ----------
    def update_selected_plane(self):
        """Trouve l'avion sélectionné dans la scène."""
        self.selected_index = None
        for i, item in enumerate(self.planes):
            if item.isSelected():
                self.selected_index = i
                return

    def altitude_up(self):
        self.update_selected_plane()
        if self.selected_index is None:
            self.statusBar().showMessage("Sélectionne un avion d'abord", 1200)
            return

        st = self.states[self.selected_index]
        if st.altitude < 3:
            st.altitude += 1
            self.recolor_plane(self.selected_index)
            self.statusBar().showMessage(f"Altitude avion -> {st.altitude}", 1000)

    def altitude_down(self):
        self.update_selected_plane()
        if self.selected_index is None:
            self.statusBar().showMessage("Sélectionne un avion d'abord", 1200)
            return

        st = self.states[self.selected_index]
        if st.altitude > 1:
            st.altitude -= 1
            self.recolor_plane(self.selected_index)
            self.statusBar().showMessage(f"Altitude avion -> {st.altitude}", 1000)

    # ---------- COLLISIONS ----------
    def handle_collisions(self):
        to_remove = set()

        for i in range(len(self.states)):
            if i in to_remove:
                continue
            for j in range(i + 1, len(self.states)):
                if j in to_remove:
                    continue

                a = self.states[i]
                b = self.states[j]

                # collision seulement si même altitude
                if a.altitude != b.altitude:
                    continue

                d = math.hypot(a.x - b.x, a.y - b.y)
                if d < self.collision_dist:
                    to_remove.add(i)
                    to_remove.add(j)

        if not to_remove:
            return

        for idx in sorted(to_remove, reverse=True):
            item = self.planes.pop(idx)
            self.states.pop(idx)
            self.scene.removeItem(item)

        self.statusBar().showMessage(f"Collision ! {len(to_remove)} avions supprimés.", 1500)

    # ---------- SIMULATION ----------
    def tick(self):
        dt = self.clock.elapsed() / 1000.0
        self.clock.restart()
        if dt <= 0:
            return

        # mettre à jour la sélection
        self.update_selected_plane()

        # mouvement
        for item, st in zip(self.planes, self.states):
            rad = math.radians(st.heading_deg)
            nx = st.x + st.speed * math.cos(rad) * dt
            ny = st.y + st.speed * math.sin(rad) * dt

            dx = nx - self.cx
            dy = ny - self.cy
            dist = math.hypot(dx, dy)

            # rebond sur le bord du cercle
            if dist >= self.R:
                nx_norm = dx / dist if dist != 0 else 1
                ny_norm = dy / dist if dist != 0 else 0

                vx = math.cos(rad)
                vy = math.sin(rad)

                dot = vx * nx_norm + vy * ny_norm
                rvx = vx - 2 * dot * nx_norm
                rvy = vy - 2 * dot * ny_norm

                st.heading_deg = (math.degrees(math.atan2(rvy, rvx))) % 360

                nx = self.cx + (self.R - 1) * nx_norm
                ny = self.cy + (self.R - 1) * ny_norm

            st.x, st.y = nx, ny

            b = item.boundingRect()
            item.setPos(st.x - b.width() / 2, st.y - b.height() / 2)
            item.setRotation(st.heading_deg)

        # collisions après déplacement
        self.handle_collisions()

    # ---------- SLOT BOUTON DESIGNER ----------
    @Slot()
    def demo(self):
        """Si pushButton.clicked -> MainWindow.demo() existe dans ui_demo.py."""
        self.add_one_plane()
        self.statusBar().showMessage("Nouvel avion ajouté", 1200)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
