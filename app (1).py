# app.py
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

from ui_demo import Ui_MainWindow      # généré depuis demo.ui
import resources_rc                    # pour :/img/plane.png


# ----------------------------------------------------------------------
#  Modèle : état d'un avion
# ----------------------------------------------------------------------
@dataclass
class PlaneState:
    x: float
    y: float
    heading_deg: float   # cap (0° vers la droite, 90° vers le bas)
    speed: float         # pixels / seconde
    altitude: int        # 1, 2, 3


# ----------------------------------------------------------------------
#  Fenêtre principale
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # -- Récupérer le QGraphicsView --
        self.view: QGraphicsView = getattr(self.ui, "radarView", None)
        if self.view is None:
            raise RuntimeError("Aucun QGraphicsView 'radarView' trouvé dans l'UI")

        # Scène 2D
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)

        # Listes d'avions
        self.planes: list[QGraphicsPixmapItem] = []
        self.states: list[PlaneState] = []
        self.selected_index: int | None = None

        # paramètres collisions
        self.collision_distance = 40.0

        # Clock + timer simulation
        self.clock = QElapsedTimer()
        self.timer = QTimer(self)
        self.timer.setInterval(50)     # 20 Hz
        self.timer.timeout.connect(self.on_tick)

        # Connexions des boutons (Altitude)
        self.ui.btnUp.clicked.connect(self.raise_altitude)
        self.ui.btnDown.clicked.connect(self.lower_altitude)

        # Connexions des boutons (orientation uniquement)
        # 0° = droite, 90° = bas, 180° = gauche, 270° = haut
        self.ui.btnMoveUp.clicked.connect(
            lambda: self.set_heading_selected(270)
        )
        self.ui.btnMoveDown.clicked.connect(
            lambda: self.set_heading_selected(90)
        )
        self.ui.btnMoveLeft.clicked.connect(
            lambda: self.set_heading_selected(180)
        )
        self.ui.btnMoveRight.clicked.connect(
            lambda: self.set_heading_selected(0)
        )

        # Connexion sur la sélection dans la scène
        self.scene.selectionChanged.connect(self.on_selection_changed)

        # On diffère l'initialisation du radar pour que la vue ait sa vraie taille
        QTimer.singleShot(0, self.finish_setup)

    # ------------------------------------------------------------------
    #  Initialisation complète (appelée après que la fenêtre soit posée)
    # ------------------------------------------------------------------
    def finish_setup(self):
        # Calculer taille + centre + rayon du radar
        self.update_radar_geometry()

        # Dessiner le radar (fond, cercles, degrés…)
        self.draw_radar()

        # Préparer les pixmaps colorés pour les 3 niveaux
        base = QPixmap(":/img/plane.png")
        if base.isNull():
            raise RuntimeError("Image :/img/plane.png introuvable (resources.qrc)")

        # facteur de taille de l'avion
        self.plane_scale = 0.10

        # Couleurs selon altitude
        self.alt_colors: dict[int, QColor] = {
            1: QColor(0, 255, 0),     # vert
            2: QColor(0, 150, 255),   # bleu
            3: QColor(255, 60, 60),   # rouge
        }

        # Pixmaps teintés
        self.alt_pixmaps: dict[int, QPixmap] = {
            level: self.tint_pixmap(base, color)
            for level, color in self.alt_colors.items()
        }

        # Créer quelques avions au hasard
        for _ in range(5):
            self.add_one_plane()

        # Lancer la simulation
        self.clock.start()
        self.timer.start()

    # ------------------------------------------------------------------
    #  Géométrie du radar (taille de la scène, centre et rayon)
    # ------------------------------------------------------------------
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
        self.R = min(self.W, self.H) / 2.0 - 40.0  # marge de 40 px

    # ------------------------------------------------------------------
    #  Dessin du radar (cercle + axes + degrés)
    # ------------------------------------------------------------------
    def draw_radar(self):
        # Effacer ce qui est déjà dans la scène (avions compris)
        self.scene.clear()
        self.planes.clear()
        self.states.clear()
        self.selected_index = None

        # Cercle principal
        bg = QGraphicsEllipseItem(self.cx - self.R,
                                  self.cy - self.R,
                                  2 * self.R,
                                  2 * self.R)
        bg.setPen(QPen(Qt.white, 2))
        bg.setBrush(QBrush(Qt.black))
        self.scene.addItem(bg)

        # Cercles internes
        for k in range(1, 4):
            r = self.R * k / 4.0
            c = QGraphicsEllipseItem(self.cx - r,
                                     self.cy - r,
                                     2 * r,
                                     2 * r)
            c.setPen(QPen(Qt.darkGray, 1, Qt.DashLine))
            self.scene.addItem(c)

        # Axes X/Y
        axis_pen = QPen(Qt.gray, 1)
        self.scene.addLine(self.cx - self.R, self.cy,
                           self.cx + self.R, self.cy, axis_pen)
        self.scene.addLine(self.cx, self.cy - self.R,
                           self.cx, self.cy + self.R, axis_pen)

        # Graduations + labels degrés
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
                label.setPos(tx - br.width() / 2.0, ty - br.height() / 2.0)
                self.scene.addItem(label)

    # ------------------------------------------------------------------
    #  Création d'un pixmap teinté (vert / bleu / rouge)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    #  Ajout d'un avion aléatoire
    # ------------------------------------------------------------------
    def add_one_plane(self):
        # Choisir altitude / couleur
        altitude = random.randint(1, 3)
        pix = self.alt_pixmaps[altitude]

        item = QGraphicsPixmapItem(pix)

        # mise à l’échelle
        item.setScale(self.plane_scale)

        # Décaler le pixmap pour que son centre soit en (0,0)
        item.setOffset(-pix.width() / 2.0, -pix.height() / 2.0)

        # Pivot de rotation au centre
        item.setTransformOriginPoint(0, 0)

        # sélection possible
        item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.scene.addItem(item)

        # Position aléatoire dans le disque (80% du rayon)
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.R * 0.8)
        x = self.cx + radius * math.cos(angle)
        y = self.cy + radius * math.sin(angle)

        heading = random.uniform(0, 360)

        # >>> VITESSE PLUS LENTE <<<
        speed = random.uniform(40, 80)  # px/s (au lieu de 80–160)

        state = PlaneState(x=x, y=y, heading_deg=heading, speed=speed, altitude=altitude)
        self.states.append(state)
        self.planes.append(item)

        # Placement graphique
        self.update_plane_graphic(len(self.states) - 1)

    # ------------------------------------------------------------------
    #  Mise à jour d'un avion (position + rotation + pixmap couleur)
    # ------------------------------------------------------------------
    def update_plane_graphic(self, idx: int):
        item = self.planes[idx]
        st = self.states[idx]

        # Mettre le bon pixmap selon l'altitude
        pix = self.alt_pixmaps[st.altitude]
        item.setPixmap(pix)

        # Z-value pour éviter que tout se confonde : altitude plus haute au-dessus
        item.setZValue(st.altitude)

        # Comme le centre du pixmap est en (0,0),
        # on pose l’avion directement en (x, y)
        item.setPos(st.x, st.y)
        item.setRotation(st.heading_deg)

    # ------------------------------------------------------------------
    #  Simulation (timer)
    # ------------------------------------------------------------------
    def on_tick(self):
        if not self.clock.isValid():
            return
        dt = self.clock.elapsed() / 1000.0
        self.clock.restart()
        if dt <= 0:
            return

        # Mouvement + rebond sur le bord du radar
        for idx, (item, st) in enumerate(zip(self.planes, self.states)):
            rad = math.radians(st.heading_deg)
            nx = st.x + st.speed * math.cos(rad) * dt
            ny = st.y + st.speed * math.sin(rad) * dt

            dx = nx - self.cx
            dy = ny - self.cy
            dist = math.hypot(dx, dy)

            if dist >= self.R - 5.0:
                # Normal au bord
                nx_norm = dx / dist if dist != 0 else 1.0
                ny_norm = dy / dist if dist != 0 else 0.0

                # vecteur vitesse unitaire
                vx = math.cos(rad)
                vy = math.sin(rad)

                # réflexion : v' = v - 2*(v·n)*n
                dot = vx * nx_norm + vy * ny_norm
                rvx = vx - 2 * dot * nx_norm
                rvy = vy - 2 * dot * ny_norm

                st.heading_deg = (math.degrees(math.atan2(rvy, rvx))) % 360

                # replacer à l'intérieur
                nx = self.cx + (self.R - 6.0) * nx_norm
                ny = self.cy + (self.R - 6.0) * ny_norm

            st.x, st.y = nx, ny
            self.update_plane_graphic(idx)

        # Gestion des collisions (même altitude seulement)
        self.handle_collisions()

    # ------------------------------------------------------------------
    #  Collisions : si 2 avions se touchent ET même altitude → disparus
    # ------------------------------------------------------------------
    def handle_collisions(self):
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

        if not to_remove:
            return

        # Supprimer en partant de la fin pour ne pas casser les indices
        for idx in sorted(to_remove, reverse=True):
            item = self.planes.pop(idx)
            self.states.pop(idx)
            self.scene.removeItem(item)

            if self.selected_index == idx:
                self.selected_index = None
            elif self.selected_index is not None and self.selected_index > idx:
                self.selected_index -= 1

    # ------------------------------------------------------------------
    #  Gestion de la sélection d'un avion (clic dans la scène)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    #  Boutons "Monter" / "descendre" (altitude)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    #  Changer la direction de l'avion sélectionné
    # ------------------------------------------------------------------
    def set_heading_selected(self, heading_deg: float):
        if self.selected_index is None:
            return
        st = self.states[self.selected_index]
        st.heading_deg = heading_deg % 360
        self.update_plane_graphic(self.selected_index)


# ----------------------------------------------------------------------
#  Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
