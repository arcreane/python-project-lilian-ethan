import sys
import math
import random
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
)
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QPen,
    QBrush,
    QFont,
    QColor,
)
from PySide6.QtCore import Qt, QTimer, QElapsedTimer

from ui_demo import Ui_MainWindow

from runway import RunwayItem
from score_item import ScoreItem



class RadarItem:
    """
    "Manager" du radar : il crée tous les items (cercles, axes, graduations)
    dans la scène et les conserve pour pouvoir les redessiner.
    """

    def __init__(self, scene: QGraphicsScene, cx: float, cy: float, R: float):
        self.scene = scene
        self.cx = cx
        self.cy = cy
        self.R = R
        self.items: list = []
        self.draw()

    def clear(self):
        for it in self.items:
            self.scene.removeItem(it)
        self.items.clear()

    def draw(self):
        import math

        self.clear()

        # Cercle principal
        bg = QGraphicsEllipseItem(
            self.cx - self.R,
            self.cy - self.R,
            2 * self.R,
            2 * self.R,
        )
        bg.setPen(QPen(Qt.white, 2))
        bg.setBrush(QBrush(Qt.black))
        bg.setZValue(0.0)
        self.scene.addItem(bg)
        self.items.append(bg)

        # Cercles internes
        for k in range(1, 4):
            r = self.R * k / 4.0
            c = QGraphicsEllipseItem(
                self.cx - r, self.cy - r, 2 * r, 2 * r
            )
            c.setPen(QPen(Qt.darkGray, 1, Qt.DashLine))
            c.setZValue(0.0)
            self.scene.addItem(c)
            self.items.append(c)

        # Axes
        axis_pen = QPen(Qt.gray, 1)
        line_h = self.scene.addLine(
            self.cx - self.R, self.cy,
            self.cx + self.R, self.cy,
            axis_pen,
        )
        line_v = self.scene.addLine(
            self.cx, self.cy - self.R,
            self.cx, self.cy + self.R,
            axis_pen,
        )
        self.items.extend([line_h, line_v])

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
                label.setPos(tx - br.width() / 2.0, ty - br.height() / 2.0)
                label.setZValue(0.0)
                self.scene.addItem(label)
                self.items.append(label)

    def reposition(self, cx: float, cy: float, R: float):
        self.cx = cx
        self.cy = cy
        self.R = R
        self.draw()



@dataclass
class PlaneState:
    x: float
    y: float
    heading_deg: float   # 0° = droite, 90° = bas, 180° = gauche, 270° = haut
    speed: float         # pixels / seconde
    altitude: int        # 1, 2, 3

class MainWindow(QMainWindow):#début de la soufrance intense qui est le self
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

#interface graphique de la scène
        self.view: QGraphicsView = getattr(self.ui, "radarView", None)
        if self.view is None:
            raise RuntimeError("Aucun QGraphicsView 'radarView' trouvé dans l'UI")

        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)

#liste des avions ainsi que leur état
        self.planes: list[QGraphicsPixmapItem] = []
        self.states: list[PlaneState] = []
        self.selected_index: int | None = None

#paramètres
        self.heading_step = 10.0
        self.collision_distance = 35
        self.plane_scale = 0.10

#radar
        self.radar: RadarItem | None = None
        self.runway: RunwayItem | None = None
        self.score_item: ScoreItem | None = None
#temps que je maitrise à moitié
        self.clock = QElapsedTimer()
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.on_tick)

#bouton des déplacements de l'avion relier à QT
        self.ui.btnUp.clicked.connect(self.raise_altitude)
        self.ui.btnDown.clicked.connect(self.lower_altitude)


        self.ui.btnMoveLeft.clicked.connect(
            lambda: self.rotate_selected(-self.heading_step)
        )
        self.ui.btnMoveRight.clicked.connect(
            lambda: self.rotate_selected(self.heading_step)
        )
        self.ui.btnMoveUp.clicked.connect(self.orient_selected_up)
        self.ui.btnMoveDown.clicked.connect(self.orient_selected_down)

#selection de l'avion
        self.scene.selectionChanged.connect(self.on_selection_changed)


        self.base_plane_pix: QPixmap | None = None
        self.alt_pixmaps: dict[int, QPixmap] = {}
        self.alt_colors: dict[int, QColor] = {}

#radar géomérie
        self.W = self.H = 0.0
        self.cx = self.cy = 0.0
        self.R = 0.0


        QTimer.singleShot(0, self.finish_setup)


    def finish_setup(self):
        self.update_radar_geometry()
        self.scene.clear()


        self.radar = RadarItem(self.scene, self.cx, self.cy, self.R)


        self.runway = RunwayItem(scale=0.12)
        ry = self.cy + self.R * 0.35
        self.runway.setPos(self.cx, ry)
        self.scene.addItem(self.runway)

        self.score_item = ScoreItem()
        self.scene.addItem(self.score_item)
        self.position_score()


        base = QPixmap(":/img/plane.png")
        if base.isNull():
            raise RuntimeError("Image :/img/plane.png introuvable dans resources.qrc")
        self.base_plane_pix = base

        self.alt_colors = {
            1: QColor(0, 255, 0),
            2: QColor(0, 150, 255),
            3: QColor(255, 60, 60),
        }
        self.alt_pixmaps = {
            level: self.tint_pixmap(base, color)
            for level, color in self.alt_colors.items()
        }

        # Avions initiaux
        self.planes.clear()
        self.states.clear()
        for _ in range(5):
            self.add_one_plane()

        self.clock.start()
        self.timer.start()

#géométrie du radar qui s'update
    def update_radar_geometry(self):
        vw = self.view.viewport().width()
        vh = self.view.viewport().height()
        if vw <= 0:
            vw = 800
        if vh <= 0:
            vh = 600

        self.W, self.H = float(vw), float(vh)
        self.scene.setSceneRect(0, 0, self.W, self.H)
        self.cx, self.cy = self.W / 2.0, self.H / 2.0
        self.R = min(self.W, self.H) / 2.0 - 40.0

#position du score
    def position_score(self):
        if self.score_item is None:
            return
        x = self.cx - 80
        y = self.cy - self.R - 40
        self.score_item.setPos(x, y)

#utilise QPainter pour essayer recolorer les avions en fonctions de l'altitude
    @staticmethod
    def tint_pixmap(pix: QPixmap, color: QColor) -> QPixmap:
        result = QPixmap(pix.size())
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, pix)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(result.rect(), color)
        painter.end()
        return result

#créer un avion en fonction de paramètre aléatoire du style :  l'altitude, position, direction et vitesse
    def add_one_plane(self):
        altitude = random.randint(1, 3)
        pix = self.alt_pixmaps[altitude]

        item = QGraphicsPixmapItem(pix)
        item.setScale(self.plane_scale)
        item.setOffset(-pix.width() / 2, -pix.height() / 2)
        item.setTransformOriginPoint(0, 0)
        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
        item.setZValue(1.0)
        self.scene.addItem(item)

        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.R * 0.8)
        x = self.cx + radius * math.cos(angle)
        y = self.cy + radius * math.sin(angle)

        heading = random.uniform(0, 360)
        speed = random.uniform(40, 80)

        st = PlaneState(x=x, y=y, heading_deg=heading, speed=speed, altitude=altitude)
        self.states.append(st)
        self.planes.append(item)
        self.update_plane_graphic(len(self.states) - 1)


    def update_plane_graphic(self, idx: int):
        item = self.planes[idx]
        st = self.states[idx]
        item.setPixmap(self.alt_pixmaps[st.altitude])
        item.setZValue(1.0 + 0.1 * st.altitude)
        item.setPos(st.x, st.y)
        item.setRotation(st.heading_deg)

    # Je mets à jour la position de l'avion, la vitesse etc avec le temps
    def on_tick(self):
        if not self.clock.isValid():
            return
        dt = self.clock.elapsed() / 1000.0
        self.clock.restart()
        if dt <= 0:
            return

        # Mouvement + rebond
        for idx, st in enumerate(self.states):
            rad = math.radians(st.heading_deg)
            nx = st.x + st.speed * math.cos(rad) * dt
            ny = st.y + st.speed * math.sin(rad) * dt

            dx = nx - self.cx
            dy = ny - self.cy
            dist = math.hypot(dx, dy)

            if dist >= self.R - 5.0:
                nx_norm = dx / dist if dist != 0 else 1.0
                ny_norm = dy / dist if dist != 0 else 0.0

                vx = math.cos(rad)
                vy = math.sin(rad)
                dot = vx * nx_norm + vy * ny_norm
                rvx = vx - 2 * dot * nx_norm
                rvy = vy - 2 * dot * ny_norm

                st.heading_deg = (math.degrees(math.atan2(rvy, rvx))) % 360
                nx = self.cx + (self.R - 6.0) * nx_norm
                ny = self.cy + (self.R - 6.0) * ny_norm

            st.x, st.y = nx, ny
            self.update_plane_graphic(idx)

        self.handle_collisions()
        self.handle_runway_landings()

    def handle_collisions(self):
        if self.score_item is None:
            return

        to_remove: set[int] = set()
        n = len(self.states)

        for i in range(n):
            if i in to_remove:
                continue
            for j in range(i + 1, n):
                if j in to_remove:
                    continue
                si = self.states[i]
                sj = self.states[j]
                if si.altitude != sj.altitude:
                    continue
                dx = si.x - sj.x
                dy = si.y - sj.y
                dist = math.hypot(dx, dy)
                if dist < self.collision_distance:
                    to_remove.add(i)
                    to_remove.add(j)

        removed = 0
        for k, idx in enumerate(sorted(to_remove)):
            self.remove_plane_at_index(idx - k)
            removed += 1

        if removed > 0:
            penalty = -(removed // 2)
            if penalty != 0:
                self.score_item.add(penalty)

#détection de l'arrivé de l'avion sur la piste avec + au score.
    def handle_runway_landings(self):

        if self.runway is None or self.score_item is None:
            return

        runway_rect = self.runway.mapToScene(
            self.runway.boundingRect()
        ).boundingRect()

        to_remove = []
        for idx, st in enumerate(self.states):
            if st.altitude != 1:
                continue
            if runway_rect.contains(st.x, st.y):
                to_remove.append(idx)

        landed = 0
        for k, idx in enumerate(sorted(to_remove)):
            self.remove_plane_at_index(idx - k)
            landed += 1

        if landed > 0:

            self.score_item.add(landed)


            per_plane = 3 if self.score_item.value >= 3 else 2

            for _ in range(landed * per_plane):
                self.add_one_plane()


    def remove_plane_at_index(self, idx: int):
        item = self.planes.pop(idx)
        self.scene.removeItem(item)
        self.states.pop(idx)

        if self.selected_index == idx:
            self.selected_index = None
        elif self.selected_index is not None and self.selected_index > idx:
            self.selected_index -= 1


    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self.selected_index = None
            return

        item = selected_items[0]
        try:
            idx = self.planes.index(item)
        except ValueError:
            self.selected_index = None
            return

        self.selected_index = idx


    def raise_altitude(self):
        if self.selected_index is None:
            return
        st = self.states[self.selected_index]
        if st.altitude < 3:
            st.altitude += 1
            self.update_plane_graphic(self.selected_index)

    def lower_altitude(self):
        if self.selected_index is None:
            return
        st = self.states[self.selected_index]
        if st.altitude > 1:
            st.altitude -= 1
            self.update_plane_graphic(self.selected_index)


    def rotate_selected(self, delta_deg: float):
        if self.selected_index is None:
            return
        st = self.states[self.selected_index]
        st.heading_deg = (st.heading_deg + delta_deg) % 360
        self.update_plane_graphic(self.selected_index)

    def orient_selected_up(self):
        if self.selected_index is None:
            return
        st = self.states[self.selected_index]
        st.heading_deg = 270.0
        self.update_plane_graphic(self.selected_index)

    def orient_selected_down(self):
        if self.selected_index is None:
            return
        st = self.states[self.selected_index]
        st.heading_deg = 90.0
        self.update_plane_graphic(self.selected_index)


    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.update_radar_geometry()

        if self.radar is not None:
            self.radar.reposition(self.cx, self.cy, self.R)

        if self.runway is not None:
            ry = self.cy + self.R * 0.35
            self.runway.setPos(self.cx, ry)

        self.position_score()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
