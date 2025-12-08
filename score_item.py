# score_item.py
from PySide6.QtWidgets import QGraphicsTextItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QRectF

#permet de mettre le score à 0 par défaut puis augmenter et descendre, on peut aller en négatif prcq pourquoi pas.
class ScoreItem(QGraphicsTextItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.value = 0

        self.setDefaultTextColor(Qt.white)
        self.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.setZValue(2.0)

        self._update_text()

    #permet d'ajouter ou retirer des points au score.
    def add(self, delta: int) -> None:
        self.value += delta
        self._update_text()
#on rest tout pour revenir à 0
    def reset(self) -> None:
        self.value = 0
        self._update_text()

    def _update_text(self) -> None:
        self.setPlainText(f"Score : {self.value}")

    #positionnement
    def update_position(self, view_rect: QRectF,
                        margin_x: float = 40,
                        margin_y: float = 40) -> None:
        """
        Place le score dans le coin supérieur droit de view_rect.
        """
        br = self.boundingRect()
        x = view_rect.right() - margin_x - br.width()
        y = view_rect.top() + margin_y
        self.setPos(x, y)
