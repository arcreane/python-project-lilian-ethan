# utils.py

from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import Qt


def tint_pixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """Applique une teinte colorée sur un QPixmap."""
    if pixmap.isNull():
        return QPixmap()  # sécurité si l'image n'existe pas

    # image transparente finale
    result = QPixmap(pixmap.size())
    result.fill(Qt.transparent)

    # peinture
    painter = QPainter(result)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)

    # applique la couleur
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), color)

    painter.end()

    return result


def safe_disconnect(signal):
    """Déconnecte un signal sans erreur."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        try:
            signal.disconnect()
        except (TypeError, RuntimeError):
            pass
