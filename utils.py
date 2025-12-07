# utils.py
from PySide6.QtGui import QPixmap, QColor

def tint_pixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """Applique une teinte unie sur un QPixmap."""
    tinted = QPixmap(pixmap.size())
    tinted.fill(color)

    result = QPixmap(pixmap.size())
    result.fill(Qt.transparent)

    painter = QPainter(result)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
    painter.drawPixmap(0, 0, tinted)
    painter.end()

    return result
