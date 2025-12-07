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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(894, 713)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.bntUp = QPushButton(self.centralwidget)
        self.bntUp.setObjectName(u"bntUp")
        self.bntUp.setGeometry(QRect(600, 80, 79, 24))
        self.btnMoveLeft = QPushButton(self.centralwidget)
        self.btnMoveLeft.setObjectName(u"btnMoveLeft")
        self.btnMoveLeft.setGeometry(QRect(540, 250, 79, 24))
        self.btnMoveRight = QPushButton(self.centralwidget)
        self.btnMoveRight.setObjectName(u"btnMoveRight")
        self.btnMoveRight.setGeometry(QRect(670, 250, 79, 24))
        self.btnDown = QPushButton(self.centralwidget)
        self.btnDown.setObjectName(u"btnDown")
        self.btnDown.setGeometry(QRect(600, 120, 79, 24))
        self.btnMoveUp = QPushButton(self.centralwidget)
        self.btnMoveUp.setObjectName(u"btnMoveUp")
        self.btnMoveUp.setGeometry(QRect(600, 220, 79, 24))
        self.btnMoveDown = QPushButton(self.centralwidget)
        self.btnMoveDown.setObjectName(u"btnMoveDown")
        self.btnMoveDown.setGeometry(QRect(600, 280, 79, 24))
        self.radarView = QGraphicsView(self.centralwidget)
        self.radarView.setObjectName(u"radarView")
        self.radarView.setGeometry(QRect(20, 20, 501, 621))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 894, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.bntUp.setText(QCoreApplication.translate("MainWindow", u"Monter", None))
        self.btnMoveLeft.setText(QCoreApplication.translate("MainWindow", u"gauche", None))
        self.btnMoveRight.setText(QCoreApplication.translate("MainWindow", u"droite", None))
        self.btnDown.setText(QCoreApplication.translate("MainWindow", u"descendre", None))
        self.btnMoveUp.setText(QCoreApplication.translate("MainWindow", u"haut", None))
        self.btnMoveDown.setText(QCoreApplication.translate("MainWindow", u"bas", None))
    # retranslateUi

