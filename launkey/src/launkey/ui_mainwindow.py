################################################################################
# MainWindow UI setup for Launkey
# This file is no longer auto-generated. You can safely edit it.
################################################################################

from PySide6.QtCore import (QCoreApplication, QRect, QSize, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QCursor)
from PySide6.QtWidgets import (
    QAbstractItemView, QAbstractScrollArea, QFrame, QGroupBox, QHBoxLayout,
    QLayout, QMainWindow, QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QScrollArea, QGridLayout
)
from .custom_layouts import DynamicGridLayout  # Import the custom layout class

class Ui_MainWindow:
    def setupUi(self, MainWindow: QMainWindow):
        # Main window setup
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(800, 600))

        # Actions (menu items)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")

        # Central widget and layout
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(1)
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Left panel: Launchpad grid and Run button
        self.verticalFrame = QFrame(self.centralwidget)
        self.verticalFrame.setObjectName("verticalFrame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.verticalFrame.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.verticalFrame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)

        # Launchpad grid (9x9)
        self.tableLaunchpad = QTableWidget(self.verticalFrame)
        self.tableLaunchpad.setObjectName("tableLaunchpad")
        self.tableLaunchpad.setRowCount(9)
        self.tableLaunchpad.setColumnCount(9)
        for i in range(9):
            self.tableLaunchpad.setHorizontalHeaderItem(i, QTableWidgetItem())
            self.tableLaunchpad.setVerticalHeaderItem(i, QTableWidgetItem())
        # Example: Mark top-right cell as special (can be customized)
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.DiagCrossPattern)
        special_item = QTableWidgetItem()
        special_item.setBackground(brush)
        special_item.setFlags(
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )
        self.tableLaunchpad.setItem(0, 8, special_item)
        # Table settings for better usability
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(4)
        self.tableLaunchpad.setSizePolicy(sizePolicy2)
        self.tableLaunchpad.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
        self.tableLaunchpad.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableLaunchpad.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableLaunchpad.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableLaunchpad.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableLaunchpad.setDragEnabled(False)
        self.tableLaunchpad.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.tableLaunchpad.setAlternatingRowColors(True)
        self.tableLaunchpad.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableLaunchpad.horizontalHeader().setVisible(False)
        self.tableLaunchpad.horizontalHeader().setMinimumSectionSize(30)
        self.tableLaunchpad.horizontalHeader().setDefaultSectionSize(30)
        self.tableLaunchpad.verticalHeader().setVisible(False)
        self.tableLaunchpad.verticalHeader().setHighlightSections(True)
        self.tableLaunchpad.verticalHeader().setStretchLastSection(False)
        self.tableLaunchpad.setEnabled(False)

        self.verticalLayout.addWidget(self.tableLaunchpad)

        # Run button
        self.buttonRun = QPushButton(self.verticalFrame)
        self.buttonRun.setObjectName("buttonRun")
        self.buttonRun.setEnabled(False)
        self.verticalLayout.addWidget(self.buttonRun)

        self.horizontalLayout.addWidget(self.verticalFrame)

        # Right panel: Template group
        self.groupTemplates = QGroupBox(self.centralwidget)
        self.groupTemplates.setObjectName("groupTemplates")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy3.setHorizontalStretch(2)
        self.groupTemplates.setSizePolicy(sizePolicy3)
        self.groupTemplates.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Add layout to groupTemplates
        self.groupTemplatesLayout = QVBoxLayout(self.groupTemplates)
        self.groupTemplatesLayout.setObjectName("groupTemplatesLayout")
        self.groupTemplatesLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.addWidget(self.groupTemplates)

        MainWindow.setCentralWidget(self.centralwidget)

        # Scroll area for templates
        self.scrollAreaTemplates = QScrollArea(self.groupTemplates)
        self.scrollAreaTemplates.setObjectName("scrollAreaTemplates")
        self.scrollAreaTemplates.setWidgetResizable(True)
        self.groupTemplatesLayout.addWidget(self.scrollAreaTemplates)

        # Add FlowLayout to groupTemplates
        self.contentTemplates = QWidget()
        self.contentTemplates.setObjectName("contentTemplates")
        self.gridLayoutTemplates = DynamicGridLayout(self.contentTemplates, min_col_width=150, min_row_height=130)
        self.gridLayoutTemplates.setSpacing(4)
        self.contentTemplates.setLayout(self.gridLayoutTemplates)
        self.scrollAreaTemplates.setWidget(self.contentTemplates)

        # Add "add template" button
        self.buttonAddTemplate = QPushButton()
        self.buttonAddTemplate.setObjectName("buttonAddTemplate")
        self.gridLayoutTemplates.addWidget(self.buttonAddTemplate)

        # Status bar
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Menu bar
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 24))
        self.menuConfig = QMenu(self.menubar)
        self.menuConfig.setObjectName("menuConfig")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuConfig.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuConfig.addAction(self.actionSave)
        self.menuConfig.addAction(self.actionLoad)
        self.menuConfig.addSeparator()
        self.menuConfig.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)
        # Connect signals if needed
        # QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        # Window and menu texts
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Launkey"))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", "Save"))
        self.actionLoad.setText(QCoreApplication.translate("MainWindow", "Load"))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", "About"))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", "Settings"))
        # Table headers
        for i in range(8):
            self.tableLaunchpad.horizontalHeaderItem(i).setText(QCoreApplication.translate("MainWindow", "Button"))  # type: ignore
        self.tableLaunchpad.horizontalHeaderItem(8).setText(QCoreApplication.translate("MainWindow", "Round Button")) # type: ignore
        self.tableLaunchpad.verticalHeaderItem(0).setText(QCoreApplication.translate("MainWindow", "Round Button"))
        for i in range(1, 9):
            self.tableLaunchpad.verticalHeaderItem(i).setText(QCoreApplication.translate("MainWindow", "Button"))
        # Button and group titles
        self.buttonRun.setText(QCoreApplication.translate("MainWindow", "Run"))
        self.buttonAddTemplate.setText(QCoreApplication.translate("MainWindow", "Add Template"))
        self.groupTemplates.setTitle(QCoreApplication.translate("MainWindow", "Templates"))
        self.menuConfig.setTitle(QCoreApplication.translate("MainWindow", "Configuration"))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help"))
    # retranslateUi
