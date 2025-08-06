################################################################################
# Dialog UI setup for Launkey
# This file is no longer auto-generated. You can safely edit it.
################################################################################

from PySide6.QtCore import QCoreApplication, QSize, QMetaObject, Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QGridLayout, QHBoxLayout, QListWidget, QPushButton,
    QScrollArea, QSizePolicy, QWidget
)
from .custom_layouts import CenterGridLayout

class Ui_Dialog:
    """
    Main dialog UI for template management in Launkey.
    """
    def setupUi(self, dialog: QDialog):
        if not dialog.objectName():
            dialog.setObjectName("Dialog")
        dialog.resize(800, 600)
        dialog.setMinimumSize(QSize(800, 600))

        # Main horizontal layout
        self.mainLayout = QHBoxLayout(dialog)
        self.mainLayout.setObjectName("mainLayout")

        # List of templates
        self.templateList = QListWidget(dialog)
        self.templateList.setObjectName("templateList")
        templateListPolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        templateListPolicy.setHorizontalStretch(7)
        self.templateList.setSizePolicy(templateListPolicy)
        self.mainLayout.addWidget(self.templateList)

        # Vertical separator
        self.separator = QFrame(dialog)
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.mainLayout.addWidget(self.separator)

        # Scroll area for template details
        self.scrollArea = QScrollArea(dialog)
        self.scrollArea.setObjectName("scrollArea")
        scrollAreaPolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        scrollAreaPolicy.setHorizontalStretch(10)
        self.scrollArea.setSizePolicy(scrollAreaPolicy)
        self.scrollArea.setWidgetResizable(True)

        # Widget inside scroll area
        self.scrollAreaWidget = QWidget()
        self.scrollAreaWidget.setObjectName("scrollAreaWidget")
        self.gridLayout = CenterGridLayout(self.scrollAreaWidget)
        self.scrollAreaWidget.setLayout(self.gridLayout)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        # Main action button (center)
        self.mainActionButton = QPushButton(self.scrollAreaWidget)
        self.mainActionButton.setObjectName("mainActionButton")
        mainActionPolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.mainActionButton.setSizePolicy(mainActionPolicy)
        self.mainActionButton.setMaximumSize(QSize(200, 200))
        self.mainActionButton.setText("Action")
        self.gridLayout.addWidget(self.mainActionButton, 0, 0)

        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.mainLayout.addWidget(self.scrollArea)

        self.retranslateUi(dialog)
        QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog: QDialog):
        dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Templates", None))
        # Button texts are set directly in setupUi for clarity
