################################################################################
# MainWindow UI setup for Launkey
# This file is no longer auto-generated. You can safely edit it.
################################################################################

from PySide6.QtCore import (QCoreApplication, QRect, QSize, Qt, QVariantAnimation)
from PySide6.QtGui import (QAction, QColor)
from PySide6.QtWidgets import (
    QFrame, QGroupBox, QHBoxLayout,
    QLayout, QMainWindow, QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget,
    QScrollArea, QSplitter, QStackedWidget
)
from .custom_layouts import DynamicGridLayout  # Import the custom layout class
from .custom_widgets import QAutoStatusBar, QLabelInfo
from .launchpad_control import LaunchpadTable

class Ui_MainWindow:
    def setupUi(self, MainWindow: QMainWindow):
        # Main window setup
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(800, 600))

        # Actions (menu items)
        # Config menu actions
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionLoad = QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionTestMode = QAction(MainWindow)
        self.actionTestMode.setObjectName("actionTestMode")
        self.actionTestMode.setCheckable(True)
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")

        # Help menu actions
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")

        # REMOVE after implementetion
        self.actionSave.setEnabled(False)
        self.actionLoad.setEnabled(False)
        self.actionSettings.setEnabled(False)
        self.actionAbout.setEnabled(False)
        # END REMOVE

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
        self.tableLaunchpad = LaunchpadTable(self.verticalFrame)
        self.verticalLayout.addWidget(self.tableLaunchpad)

        # Button panel
        self.buttonPanel = QFrame(self.verticalFrame)
        self.buttonPanel.setObjectName("buttonPanel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.buttonPanel.setSizePolicy(sizePolicy2)
        self.buttonPanel.setFrameShape(QFrame.Shape.NoFrame)
        self.buttonPanel.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout.addWidget(self.buttonPanel)
        self.buttonPanelLayout = QVBoxLayout(self.buttonPanel)
        self.buttonPanelLayout.setObjectName("buttonPanelLayout")
        self.buttonPanelLayout.setContentsMargins(0, 0, 0, 0)

        # Button splitter
        self.buttonSplitter = QSplitter(self.buttonPanel)
        self.buttonSplitter.setOrientation(Qt.Orientation.Vertical)
        self.buttonSplitter.setObjectName("buttonSplitter")
        self.buttonSplitter.setHandleWidth(10)
        self.buttonPanelLayout.addWidget(self.buttonSplitter)

        # Run button
        self.buttonRun = QPushButton(self.buttonSplitter)
        self.buttonRun.setObjectName("buttonRun")
        self.buttonRun.setEnabled(False)
        self.buttonSplitter.addWidget(self.buttonRun)

        # Reset buttons stack
        self.buttonResetStack = QStackedWidget(self.buttonSplitter)
        self.buttonResetStack.setObjectName("buttonResetStack")
        self.buttonResetStack.setEnabled(True)
        self.buttonSplitter.addWidget(self.buttonResetStack)

        # Reset button
        self.buttonReset = QPushButton(self.buttonResetStack)
        self.buttonReset.setObjectName("buttonReset")
        self.buttonReset.setAutoDefault(False)
        self.buttonReset.setStyleSheet(":active { background-color: darkred; color: white; } :disabled { background-color: black; }")
        self.buttonReset.clicked.connect(self.areYouSure)
        self.buttonResetStack.addWidget(self.buttonReset)

        # Are you sure button
        self.buttonAreYouSure = QPushButton(self.buttonResetStack)
        self.buttonAreYouSure.setObjectName("buttonAreYouSure")
        self.buttonAreYouSure.setAutoDefault(False)
        self.buttonAreYouSure.setStyleSheet(":active { background-color: red; color: white; } :disabled { background-color: black; }")
        self.buttonResetAnimation = QVariantAnimation(self.buttonAreYouSure)
        self.buttonResetAnimation.setDuration(500)
        self.buttonResetAnimation.setStartValue(QColor("red"))
        self.buttonResetAnimation.setEndValue(QColor("darkred"))
        self.buttonResetAnimation.setLoopCount(-1)  # Loop indefinitely
        self.buttonResetAnimation.valueChanged.connect(
            lambda color: self.buttonAreYouSure.setStyleSheet(
                f"background-color: {color.name()}; color: white;"
            )
        )
        self.buttonAreYouSure.clicked.connect(self.clearTable)
        self.buttonResetStack.addWidget(self.buttonAreYouSure)
        self.buttonResetStack.setCurrentWidget(self.buttonReset)

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
        self.statusbar = QAutoStatusBar(MainWindow)
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
        self.menuConfig.addAction(self.actionTestMode)
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
        self.actionTestMode.setText(QCoreApplication.translate("MainWindow", "Test Mode"))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", "About"))
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", "Settings"))

        # Button and group titles
        self.buttonRun.setText(QCoreApplication.translate("MainWindow", "Run"))
        self.buttonReset.setText(QCoreApplication.translate("MainWindow", "Reset"))
        self.buttonAreYouSure.setText(QCoreApplication.translate("MainWindow", "Are you sure???"))
        self.buttonAddTemplate.setText(QCoreApplication.translate("MainWindow", "Add Template"))
        self.groupTemplates.setTitle(QCoreApplication.translate("MainWindow", "Templates"))
        self.menuConfig.setTitle(QCoreApplication.translate("MainWindow", "Configuration"))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "Help"))
    # retranslateUi

    def areYouSure(self):
        self.buttonResetAnimation.start()
        self.buttonResetStack.setCurrentWidget(self.buttonAreYouSure)

    def clearTable(self):
        self.tableLaunchpad.resetTemplates()
        self.clearAreYouSure()

    def clearAreYouSure(self):
        self.buttonResetAnimation.stop()
        self.buttonResetStack.setCurrentWidget(self.buttonReset)

    def startRun(self):
        self.buttonResetStack.setCurrentIndex(0)
        self.buttonReset.setEnabled(False)
        self.tableLaunchpad.setEnabled(False)
        self.buttonRun.setText("Stop")
        self.statusbar.addWidget(QLabelInfo("Running", colour="green"))

    def stopRun(self) -> None:
        self.buttonRun.setText("Run")
        self.statusbar.deleteByText("Running")
        self.buttonReset.setEnabled(True)
        self.tableLaunchpad.setEnabled(True)
