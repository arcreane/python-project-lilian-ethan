# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'demo.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGridLayout, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(888, 700)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.radarView = QGraphicsView(self.centralwidget)
        self.radarView.setObjectName(u"radarView")
        self.radarView.setGeometry(QRect(-10, -10, 721, 661))
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(720, 130, 160, 176))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.btnMoveRight = QPushButton(self.gridLayoutWidget)
        self.btnMoveRight.setObjectName(u"btnMoveRight")

        self.gridLayout.addWidget(self.btnMoveRight, 5, 0, 1, 1)

        self.btnMoveDown = QPushButton(self.gridLayoutWidget)
        self.btnMoveDown.setObjectName(u"btnMoveDown")

        self.gridLayout.addWidget(self.btnMoveDown, 3, 0, 1, 1)

        self.btnDown = QPushButton(self.gridLayoutWidget)
        self.btnDown.setObjectName(u"btnDown")

        self.gridLayout.addWidget(self.btnDown, 1, 0, 1, 1)

        self.btnUp = QPushButton(self.gridLayoutWidget)
        self.btnUp.setObjectName(u"btnUp")

        self.gridLayout.addWidget(self.btnUp, 0, 0, 1, 1)

        self.btnMoveUp = QPushButton(self.gridLayoutWidget)
        self.btnMoveUp.setObjectName(u"btnMoveUp")

        self.gridLayout.addWidget(self.btnMoveUp, 2, 0, 1, 1)

        self.btnMoveLeft = QPushButton(self.gridLayoutWidget)
        self.btnMoveLeft.setObjectName(u"btnMoveLeft")

        self.gridLayout.addWidget(self.btnMoveLeft, 4, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 888, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btnMoveRight.setText(QCoreApplication.translate("MainWindow", u"droite", None))
        self.btnMoveDown.setText(QCoreApplication.translate("MainWindow", u"bas", None))
        self.btnDown.setText(QCoreApplication.translate("MainWindow", u"descendre", None))
        self.btnUp.setText(QCoreApplication.translate("MainWindow", u"Monter", None))
        self.btnMoveUp.setText(QCoreApplication.translate("MainWindow", u"haut", None))
        self.btnMoveLeft.setText(QCoreApplication.translate("MainWindow", u"gauche", None))
    # retranslateUi

