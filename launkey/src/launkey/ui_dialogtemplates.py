################################################################################
# Dialog UI setup for Launkey
# This file is no longer auto-generated. You can safely edit it.
################################################################################

from PySide6.QtCore import QCoreApplication, QSize, QMetaObject, Qt, QEvent
from PySide6.QtWidgets import (
    QDialog, QFrame, QMessageBox, QHBoxLayout, QPushButton, 
    QSizePolicy, QWidget, QVBoxLayout, QSplitter
)
from .custom_layouts import TemplateGridLayout
from .custom_widgets import ToggleButton, TemplateOptionsList
from .templates import Template

class Ui_Dialog:
    """
    Main dialog UI for template management in Launkey.
    """
    def __init__(self):
        self.mainLayout: QHBoxLayout
        self.optionsPanel: QWidget
        self.optionsList: TemplateOptionsList
        self.buttonSeparator: QSplitter
        self.closeButton: QPushButton
        self.saveButton: QPushButton
        self.separator: QFrame
        self.mainActionButton: ToggleButton
        self.editorFrame: QFrame
        self.gridLayout: TemplateGridLayout

    def setupUi(self, dialog: QDialog, template_type: Template.Type):
        if not dialog.objectName():
            dialog.setObjectName("Dialog")
        dialog.resize(800, 600)
        dialog.setMinimumSize(QSize(1000, 600))

        # Main horizontal layout
        self.mainLayout = QHBoxLayout(dialog)
        self.mainLayout.setObjectName("mainLayout")

        # Left panel for options
        self.optionsPanel = QWidget(dialog)
        self.optionsPanel.setObjectName("optionsPanel")
        optionsPanelSizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        optionsPanelSizePolicy.setHorizontalStretch(6)
        self.optionsPanel.setSizePolicy(optionsPanelSizePolicy)
        optionsPanelLayout = QVBoxLayout()
        optionsPanelLayout.setContentsMargins(0, 0, 0, 0)
        self.optionsPanel.setLayout(optionsPanelLayout)
        self.mainLayout.addWidget(self.optionsPanel)

        # List of templates
        self.optionsList = TemplateOptionsList(self.optionsPanel)
        optionsPanelLayout.addWidget(self.optionsList)  # type: ignore

        # Button separator
        self.buttonSeparator = QSplitter(dialog)
        self.buttonSeparator.setOrientation(Qt.Orientation.Horizontal)
        self.buttonSeparator.setObjectName("buttonSeparator")
        optionsPanelLayout.addWidget(self.buttonSeparator)

        # Close button
        self.closeButton = QPushButton("Close", dialog)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setAutoDefault(False)
        self.buttonSeparator.addWidget(self.closeButton)
        self.closeButton.clicked.connect(lambda: self.closeTemplateEditor(dialog))

        # Close button custom style
        self.closeButton.setStyleSheet("background-color: darkred; color: white;")

        # Save button
        self.saveButton = QPushButton("Save", dialog)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setAutoDefault(False)
        self.buttonSeparator.addWidget(self.saveButton)
        self.saveButton.clicked.connect(self.saveTemplate)

        # Save button custom style
        self.saveButton.setStyleSheet("background-color: darkgreen; color: white;")

        # Vertical separator
        self.separator = QFrame(dialog)
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.mainLayout.addWidget(self.separator)

        # Main action button (center, square)
        self.mainActionButton = ToggleButton("ActionMain", "Action")
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
        self.gridLayout = TemplateGridLayout(self.mainActionButton, self.optionsList, self.editorFrame)
        self.editorFrame.setLayout(self.gridLayout)

        self.mainLayout.addWidget(self.editorFrame)

        self.retranslateUi(dialog)
        QMetaObject.connectSlotsByName(dialog)

        dialog.closeEvent = lambda event: self.onXButtonClick(event, dialog)

    def retranslateUi(self, dialog: QDialog): # skipcq: PYL-R0201
        dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Templates", None))
        # Button texts are set directly in setupUi for clarity

    def saveTemplate(self):
        # Placeholder for save functionality
        for obj in self.optionsList.getObjects():
            print(obj)

    def onXButtonClick(self, event: QEvent, dialog: QDialog):
        self.closeTemplateEditor(dialog)
        event.setAccepted(False)

    def closeTemplateEditor(self, dialog: QDialog):
        areYouSureBox = QMessageBox()
        areYouSureBox.setIcon(QMessageBox.Icon.Warning)
        areYouSureBox.setWindowTitle("Close without saving?")
        areYouSureBox.setText("Are you sure you want to close the editor without saving?")
        areYouSureBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        areYouSureBox.setDefaultButton(QMessageBox.StandardButton.No)
        areYouSureBox.setEscapeButton(QMessageBox.StandardButton.No)
        areYouSureBox.setWindowModality(Qt.WindowModality.ApplicationModal)
        areYouSureBox.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        ret = areYouSureBox.exec()
        if ret == QMessageBox.StandardButton.Yes:
            dialog.reject()
        else:
            pass
