################################################################################
# Dialog UI setup for Launkey
# This file is no longer auto-generated. You can safely edit it.
################################################################################

import json
from pathlib import Path
from typing import List

from PySide6.QtCore import QCoreApplication, QSize, QMetaObject, Qt, QEvent, QStandardPaths
from PySide6.QtWidgets import (
    QDialog, QFrame, QMessageBox, QHBoxLayout, QPushButton, 
    QSizePolicy, QWidget, QVBoxLayout, QSplitter, QProgressDialog
)

from .custom_layouts import TemplateGridLayout
from .custom_widgets import ToggleButton, AreYouSureDialog
from .template_options_widgets import TemplateOptionsList
from .templates import Template, TemplateItem, getTemplateFolderPath, sterilizeTemplateName, getTemplateType

class Ui_Dialog:
    """
    Main dialog UI for template management in Launkey.
    """
    def __init__(self):
        self.mainLayout: QHBoxLayout
        self.optionsPanel: QWidget
        self.optionsList: TemplateOptionsList
        self.buttonSeparatorH: QSplitter
        self.closeButton: QPushButton
        self.saveButton: QPushButton
        self.separator: QFrame
        self.mainActionButton: ToggleButton
        self.editorFrame: QFrame
        self.gridLayout: TemplateGridLayout

    def loadTemplate(self, dialog: QDialog, template: List[Template | TemplateItem]):
        self.loadedTemplate = template
        template_type = getTemplateType(self.loadedTemplate)
        if template_type is None:
            self.errorMessageBox("Failed to determine template type.", "Load Template Error", dialog)
            return
        self.setupUi(dialog, template_type, self.loadedTemplate)

    def setupUi(self, dialog: QDialog, template_type: Template.Type, loadedTemplate: List[Template | TemplateItem] | None = None):
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
        self.optionsList = TemplateOptionsList(template_type, self.optionsPanel, loadedTemplate)
        optionsPanelLayout.addWidget(self.optionsList)  # type: ignore

        # Button vertical separator layout
        self.buttonSeparatorV = QSplitter(dialog)
        self.buttonSeparatorV.setOrientation(Qt.Orientation.Vertical)
        self.buttonSeparatorV.setObjectName("buttonSeparatorLayout")
        optionsPanelLayout.addWidget(self.buttonSeparatorV)

        # Close button
        self.closeButton = QPushButton("Close", dialog)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setAutoDefault(False)
        self.buttonSeparatorV.addWidget(self.closeButton)
        self.closeButton.clicked.connect(lambda: self.closeTemplateEditor(dialog))

        # Button separator
        self.buttonSeparatorH = QSplitter(dialog)
        self.buttonSeparatorH.setOrientation(Qt.Orientation.Horizontal)
        self.buttonSeparatorH.setObjectName("buttonSeparator")
        self.buttonSeparatorV.addWidget(self.buttonSeparatorH)

        # Delete button
        self.deleteButton = QPushButton("Delete", dialog)
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setAutoDefault(False)
        self.buttonSeparatorH.addWidget(self.deleteButton)
        self.deleteButton.clicked.connect(lambda: self.beforeDeleteTemplate(dialog))

        # Delete button custom style
        self.deleteButton.setStyleSheet("* { background-color: darkred; color: white; } :disabled { background-color: transparent; }")

        # Save button
        self.saveButton = QPushButton("Save", dialog)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setAutoDefault(False)
        self.buttonSeparatorH.addWidget(self.saveButton)
        self.saveButton.clicked.connect(lambda: self.saveTemplate(dialog))

        # Save button custom style
        self.saveButton.setStyleSheet("* { background-color: darkgreen; color: white; } :disabled { background-color: transparent; }")

        # Vertical separator
        self.separator = QFrame(dialog)
        self.separator.setObjectName("separator")
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.mainLayout.addWidget(self.separator)

        # Main action button (center, square)
        if not loadedTemplate:
            self.mainActionButton = ToggleButton("Button 1", "mainAction")
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

        # Flow for loading main action button
        if loadedTemplate:
            for item in loadedTemplate:
                # search for item with position (0,0)
                if isinstance(item, Template) and item.type == Template.Type.BUTTONS:
                    continue
                if isinstance(item, TemplateItem) and hasattr(item, 'location') and item.location == (0, 0):
                    self.mainActionButton = ToggleButton(item.name, item.buttonID)
                    self.mainActionButton.setObjectName("mainActionButton")
                    break

        # Centered grid layout for editor frame
        self.gridLayout = TemplateGridLayout(self.mainActionButton, self.optionsList, self.editorFrame, template=loadedTemplate)
        self.gridLayout.setupOptionsListConnection()
        self.editorFrame.setLayout(self.gridLayout)

        self.mainLayout.addWidget(self.editorFrame)

        self.retranslateUi(dialog)
        QMetaObject.connectSlotsByName(dialog)

        dialog.closeEvent = lambda event: self.onXButtonClick(event, dialog)

    def retranslateUi(self, dialog: QDialog): # skipcq: PYL-R0201
        dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Templates", None))
        # Button texts are set directly in setupUi for clarity

    def saveTemplate(self, dialog: QDialog):
        # TODO add validation for template elements!!!

        fullPath = getTemplateFolderPath()
        self.disableUIForSaving()
        
        templateName = self.optionsList.getTemplateName().strip()
        templateFileName = sterilizeTemplateName(templateName)
        filePath = fullPath / f"{templateFileName}.json"
        if filePath.exists() and not self.askForFileOverwrite(templateName):
            self.enableUIAfterSaving()
            return

        progress = QProgressDialog("Saving template...", "Cancel", 0, 100, minimumDuration=500)
        progress.setWindowTitle("Saving")
        progress.setCancelButton(None)

        pathOnSystem = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        self.saveTemplateData(filePath, pathOnSystem, progress)

        progress.setValue(100)

        dialog.accept()

    def askForFileOverwrite(self, templateName: str) -> bool:
        areYouSureBox = QMessageBox()
        areYouSureBox.setIcon(QMessageBox.Icon.Warning)
        areYouSureBox.setWindowTitle("File already exists")
        areYouSureBox.setText(f"A template named '{templateName}' already exists. Do you want to overwrite it?")
        areYouSureBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        areYouSureBox.setDefaultButton(QMessageBox.StandardButton.No)
        areYouSureBox.setEscapeButton(QMessageBox.StandardButton.No)
        areYouSureBox.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        ret = areYouSureBox.exec()
        if ret == QMessageBox.StandardButton.Yes:
            return True
        return False
    
    def enableUIAfterSaving(self):
        self.editorFrame.setDisabled(False)
        self.optionsList.setDisabled(False)

    def disableUIForSaving(self):
        self.editorFrame.setDisabled(True)
        self.optionsList.setDisabled(True)

    def saveTemplateData(self, filePath: Path, pathOnSystem: str, progress: QProgressDialog):
        progress.setValue(20)
        progress.setLabelText("Preparing template...")

        if not Path(filePath).is_relative_to(pathOnSystem): # If something went wrong with path
            raise ValueError("File path is not inside the expected system path.")

        template = self.optionsList.getObjects()

        progress.setValue(30)
        progress.setLabelText("Serializing template...")
        template_data = [obj.toDict() for obj in template]  # type: ignore

        progress.setValue(70)
        progress.setLabelText("Saving template...")
        with open(filePath, 'w') as file:
            json.dump(template_data, file)
        progress.setLabelText("Finalizing...")
        
    def onXButtonClick(self, event: QEvent, dialog: QDialog):
        self.closeTemplateEditor(dialog)
        event.setAccepted(False)

    def closeTemplateEditor(self, dialog: QDialog):
        areYouSureBox = AreYouSureDialog("Are you sure you want to close the editor without saving?")
        ret = areYouSureBox.exec()
        if ret == QMessageBox.StandardButton.Yes:
            dialog.reject()
        else:
            pass

    def beforeDeleteTemplate(self, dialog: QDialog):
        areYouSureBox = AreYouSureDialog("Are you sure you want to delete this template?")
        ret = areYouSureBox.exec()
        if ret == QMessageBox.StandardButton.Yes:
            self.deleteTemplate(dialog)
            dialog.accept()
        else:
            pass

    def deleteTemplate(self, dialog: QDialog):
        templateName = self.optionsList.getTemplateName().strip()
        fullPath = getTemplateFolderPath()
        templateFileName = sterilizeTemplateName(templateName)
        filePath = fullPath / f"{templateFileName}.json"
        try:
            if filePath.exists():
                filePath.unlink()
                print(f"Template '{templateName}' deleted successfully.")
            else:
                self.errorMessageBox(f"Template file '{templateFileName}.json' does not exist.", "Delete Template Error", dialog)
        except Exception as e:
            self.errorMessageBox(f"An error occurred while deleting the template: {e}", "Delete Template Error", dialog)

    def errorMessageBox(self, message: str, title: str, parent: QWidget | None = None):
        messagebox = QMessageBox(QMessageBox.Icon.Critical, title, message, parent=parent)
        messagebox.exec()
