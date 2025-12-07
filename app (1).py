# app.py — Radar circulaire + degrés + altitudes + collisions + déplacement manuel
import sys, math, random, warnings
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


def safe_disconnect(signal):
    """Disconnect sans warning si rien n'était connecté."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        try:
            signal.disconnect()
        except (TypeError, RuntimeError):
            pass


@dataclass
class PlaneState:
    x: float
    y: float
    heading_deg: float
    speed: float
    altitude: int   # 1, 2, 3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # récupérer la QGraphicsView (radarView OU graphicsView)
        self.view: QGraphicsView | None = (
            getattr(self.ui, "radarView", None)
            or getattr(self.ui, "graphicsView", None)
        )
        if self.view is None:
            raise RuntimeError("Aucune QGraphicsView trouvée ('radarView' ou 'graphicsView').")

        # scène
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # valeurs provisoires (recalculées dans resizeEvent)
        self.W, self.H = 800, 600
        self.scene.setSceneRect(0, 0, self.W, self.H)
        self.cx, self.cy = self.W / 2, self.H / 2
        self.R = min(self.W, self.H) * 0.45

        # radar initial
        self.draw_radar()

        # avions
        self.planes: list[QGraphicsPixmapItem] = []
        self.states: list[PlaneState] = []
        self.make_planes(n=6)

        # sélection
        self.selected_index = None

        # distance collision (avec scale=0.05)
        self.collision_dist = 18.0

        # ---------------- Connexions boutons (SAFE) ----------------

        # boutons altitude
        if hasattr(self.ui, "btnUp"):
            safe_disconnect(self.ui.btnUp.clicked)
            self.ui.btnUp.clicked.connect(self.altitude_up)

        if hasattr(self.ui, "btnDown"):
            safe_disconnect(self.ui.btnDown.clicked)
            self.ui.btnDown.clicked.connect(self.altitude_down)

        # boutons déplacement manuel (selon noms possibles)
        btn_up = getattr(self.ui, "btnMoveUp", None) or getattr(self.ui, "up", None)
        btn_down = getattr(self.ui, "btnMoveDown", None) or getattr(self.ui, "down", None)
        btn_left = getattr(self.ui, "btnMoveLeft", None) or getattr(self.ui, "left", None)
        btn_right = getattr(self.ui, "btnMoveRight", None) or getattr(self.ui, "right", None)

        if btn_up:
            safe_disconnect(btn_up.clicked)
            btn_up.clicked.connect(lambda: self.nudge_selected(0, -25))

        if btn_down:
            safe_disconnect(btn_down.clicked)
            btn_down.clicked.connect(lambda: self.nudge_selected(0, +25))

        if btn_left:
            safe_disconnect(btn_left.clicked)
            btn_left.clicked.connect(lambda: self.nudge_selected(-25, 0))

        if btn_right:
            safe_disconnect(btn_right.clicked)
            btn_right.clicked.connect(lambda: self.nudge_selected(+25, 0))

        # timer simu
        self.clock = QElapsedTimer()
        self.clock.start()

        self.timer = QTimer(self)
        self.timer.setInterval(50)  # 20 Hz
        self.timer.timeout.connect(self.tick)
        self.timer.start()

    # ---------- FIX RADAR TROP PETIT ----------
    def resizeEvent(self, event):
        super().resizeEvent(event)

        # taille réelle après layout / affichage
        self.W = self.view.viewport().width()
        self.H = self.view.viewport().height()
        self.scene.setSceneRect(0, 0, self.W, self.H)

        self.cx, self.cy = self.W / 2, self.H / 2
        self.R = min(self.W, self.H) * 0.45

        # supprimer tout sauf les avions
        for it in self.scene.items():
            if not isinstance(it, QGraphicsPixmapItem):
                self.scene.removeItem(it)

        # redessiner radar aux bonnes dimensions
        self.draw_radar()

        # recaler visuellement les avions
        for item, st in zip(self.planes, self.states):
            b = item.boundingRect()
            item.setPos(st.x - b.width()/2, st.y - b.height()/2)

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
        st = self.states[idx]
        base_pix = QPixmap(":/img/plane.png")
        tinted = tint_pixmap(base_pix, ALT_COLORS[st.altitude])
        self.planes[idx].setPixmap(tinted)

    def add_one_plane(self):
        base_pix = QPixmap(":/img/plane.png")
        if base_pix.isNull():
            raise RuntimeError("Image :/img/plane.png introuvable dans resources.qrc")

        alt = random.choice([1, 2, 3])
        tinted_pix = tint_pixmap(base_pix, ALT_COLORS[alt])

        item = QGraphicsPixmapItem(tinted_pix)
        item.setScale(0.05)
        item.setTransformOriginPoint(item.boundingRect().center())
        self.scene.addItem(item)

        # sélectionnable par clic
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

        b = item.boundingRect()
        item.setPos(x - b.width()/2, y - b.height()/2)
        item.setRotation(heading)

    # ---------- SELECTION ----------
    def update_selected_plane(self):
        self.selected_index = None
        for i, item in enumerate(self.planes):
            if item.isSelected():
                self.selected_index = i
                return

    # ---------- ALTITUDE ----------
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

    # ---------- DEPLACEMENT MANUEL ----------
    def nudge_selected(self, dx: float, dy: float):
        self.update_selected_plane()
        if self.selected_index is None:
            self.statusBar().showMessage("Sélectionne un avion d'abord", 1200)
            return

        st = self.states[self.selected_index]
        item = self.planes[self.selected_index]

        nx = st.x + dx
        ny = st.y + dy

        # garder dans le radar
        ddx = nx - self.cx
        ddy = ny - self.cy
        dist = math.hypot(ddx, ddy)
        if dist > self.R:
            ddx /= dist
            ddy /= dist
            nx = self.cx + (self.R - 2) * ddx
            ny = self.cy + (self.R - 2) * ddy

        st.x, st.y = nx, ny

        if dx != 0 or dy != 0:
            st.heading_deg = (math.degrees(math.atan2(dy, dx))) % 360

        b = item.boundingRect()
        item.setPos(st.x - b.width()/2, st.y - b.height()/2)
        item.setRotation(st.heading_deg)

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

                # pas de collision si altitudes différentes
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

        self.update_selected_plane()

        for item, st in zip(self.planes, self.states):
            rad = math.radians(st.heading_deg)
            nx = st.x + st.speed * math.cos(rad) * dt
            ny = st.y + st.speed * math.sin(rad) * dt

            dx = nx - self.cx
            dy = ny - self.cy
            dist = math.hypot(dx, dy)

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

        self.handle_collisions()

    # ---------- SLOT DESIGNER (si resté dans .ui) ----------
    @Slot()
    def demo(self):
        self.add_one_plane()
        self.statusBar().showMessage("Nouvel avion ajouté", 1200)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
