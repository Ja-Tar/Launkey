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
from .custom_widgets import SquareButton, PlusButton

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

        # Main action button (center, square)
        self.mainActionButton = SquareButton("Action")
        self.mainActionButton.setObjectName("mainActionButton")

        # Editor frame (right side)
        self.editorFrame = QFrame()
        self.editorFrame.setObjectName("editorFrame")
        self.editorFrame.setFrameShape(QFrame.Shape.StyledPanel)

        # Editor frame size policy
        editorFrameSizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        editorFrameSizePolicy.setHorizontalStretch(10)
        editorFrameSizePolicy.setVerticalStretch(0)
        self.editorFrame.setSizePolicy(editorFrameSizePolicy)

        # Centered grid layout for editor frame
        self.gridLayout = CenterGridLayout(self.mainActionButton, self.editorFrame)
        self.editorFrame.setLayout(self.gridLayout)

        self.mainLayout.addWidget(self.editorFrame)

        self.retranslateUi(dialog)
        QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog: QDialog):
        dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Templates", None))
        # Button texts are set directly in setupUi for clarity
