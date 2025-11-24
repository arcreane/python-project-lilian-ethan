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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 726)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.planeLabel = QLabel(self.centralwidget)
        self.planeLabel.setObjectName(u"planeLabel")
        self.planeLabel.setGeometry(QRect(120, 10, 121, 91))
        self.planeLabel.setPixmap(QPixmap(u":/img/plane.png"))
        self.planeLabel.setScaledContents(True)
        self.planeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(710, 100, 158, 78))
        self.btnUp = QPushButton(self.widget)
        self.btnUp.setObjectName(u"btnUp")
        self.btnUp.setGeometry(QRect(20, 10, 79, 24))
        self.btnDown = QPushButton(self.widget)
        self.btnDown.setObjectName(u"btnDown")
        self.btnDown.setGeometry(QRect(20, 40, 79, 31))
        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(690, 180, 160, 80))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.radarView = QGraphicsView(self.centralwidget)
        self.radarView.setObjectName(u"radarView")
        self.radarView.setGeometry(QRect(0, 0, 691, 671))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btnDown.clicked.connect(MainWindow.demo)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.planeLabel.setText("")
        self.btnUp.setText(QCoreApplication.translate("MainWindow", u"monter", None))
        self.btnDown.setText(QCoreApplication.translate("MainWindow", u"descendre", None))
    # retranslateUi

