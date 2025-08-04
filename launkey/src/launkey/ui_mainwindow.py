# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLayout,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(800, 600))
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName(u"actionLoad")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalFrame = QFrame(self.centralwidget)
        self.verticalFrame.setObjectName(u"verticalFrame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.verticalFrame.sizePolicy().hasHeightForWidth())
        self.verticalFrame.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.tableLaunchpad = QTableWidget(self.verticalFrame)
        if (self.tableLaunchpad.columnCount() < 9):
            self.tableLaunchpad.setColumnCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableLaunchpad.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        if (self.tableLaunchpad.rowCount() < 9):
            self.tableLaunchpad.setRowCount(9)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(3, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(4, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(5, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(6, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(7, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.tableLaunchpad.setVerticalHeaderItem(8, __qtablewidgetitem17)
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.DiagCrossPattern)
        __qtablewidgetitem18 = QTableWidgetItem()
        __qtablewidgetitem18.setBackground(brush);
        __qtablewidgetitem18.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable);
        self.tableLaunchpad.setItem(0, 8, __qtablewidgetitem18)
        self.tableLaunchpad.setObjectName(u"tableLaunchpad")
        self.tableLaunchpad.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(4)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tableLaunchpad.sizePolicy().hasHeightForWidth())
        self.tableLaunchpad.setSizePolicy(sizePolicy2)
        self.tableLaunchpad.viewport().setProperty(u"cursor", QCursor(Qt.CursorShape.ArrowCursor))
        self.tableLaunchpad.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableLaunchpad.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableLaunchpad.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableLaunchpad.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableLaunchpad.setDragEnabled(False)
        self.tableLaunchpad.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.tableLaunchpad.setAlternatingRowColors(True)
        self.tableLaunchpad.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableLaunchpad.setRowCount(9)
        self.tableLaunchpad.setColumnCount(9)
        self.tableLaunchpad.horizontalHeader().setVisible(False)
        self.tableLaunchpad.horizontalHeader().setCascadingSectionResizes(False)
        self.tableLaunchpad.horizontalHeader().setMinimumSectionSize(30)
        self.tableLaunchpad.horizontalHeader().setDefaultSectionSize(30)
        self.tableLaunchpad.verticalHeader().setVisible(False)
        self.tableLaunchpad.verticalHeader().setCascadingSectionResizes(False)
        self.tableLaunchpad.verticalHeader().setHighlightSections(True)
        self.tableLaunchpad.verticalHeader().setStretchLastSection(False)

        self.verticalLayout.addWidget(self.tableLaunchpad)

        self.buttonRun = QPushButton(self.verticalFrame)
        self.buttonRun.setObjectName(u"buttonRun")
        self.buttonRun.setEnabled(False)

        self.verticalLayout.addWidget(self.buttonRun)


        self.horizontalLayout.addWidget(self.verticalFrame)

        self.groupPresets = QGroupBox(self.centralwidget)
        self.groupPresets.setObjectName(u"groupPresets")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy3.setHorizontalStretch(2)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupPresets.sizePolicy().hasHeightForWidth())
        self.groupPresets.setSizePolicy(sizePolicy3)
        self.groupPresets.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.groupPresets)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setEnabled(True)
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        self.menuKonfig = QMenu(self.menubar)
        self.menuKonfig.setObjectName(u"menuKonfig")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuKonfig.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuKonfig.addAction(self.actionSave)
        self.menuKonfig.addAction(self.actionLoad)
        self.menuKonfig.addSeparator()
        self.menuKonfig.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Launkey", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionLoad.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        ___qtablewidgetitem = self.tableLaunchpad.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem1 = self.tableLaunchpad.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem2 = self.tableLaunchpad.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem3 = self.tableLaunchpad.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem4 = self.tableLaunchpad.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem5 = self.tableLaunchpad.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem6 = self.tableLaunchpad.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem7 = self.tableLaunchpad.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem8 = self.tableLaunchpad.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"RoundButtons", None));
        ___qtablewidgetitem9 = self.tableLaunchpad.verticalHeaderItem(0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"RoundButtons", None));
        ___qtablewidgetitem10 = self.tableLaunchpad.verticalHeaderItem(1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem11 = self.tableLaunchpad.verticalHeaderItem(2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem12 = self.tableLaunchpad.verticalHeaderItem(3)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem13 = self.tableLaunchpad.verticalHeaderItem(4)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem14 = self.tableLaunchpad.verticalHeaderItem(5)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem15 = self.tableLaunchpad.verticalHeaderItem(6)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem16 = self.tableLaunchpad.verticalHeaderItem(7)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));
        ___qtablewidgetitem17 = self.tableLaunchpad.verticalHeaderItem(8)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"Buttons", None));

        __sortingEnabled = self.tableLaunchpad.isSortingEnabled()
        self.tableLaunchpad.setSortingEnabled(False)
        self.tableLaunchpad.setSortingEnabled(__sortingEnabled)

        self.buttonRun.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.groupPresets.setTitle(QCoreApplication.translate("MainWindow", u"Presets", None))
        self.menuKonfig.setTitle(QCoreApplication.translate("MainWindow", u"Configuration", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

