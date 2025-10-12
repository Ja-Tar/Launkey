from typing import Any
from copy import deepcopy
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialog, QComboBox, QVBoxLayout, QSizePolicy,
    QFrame, QSplitter, QPushButton, QWidget
)
#from PySide6.QtGui

from .theme_loader import AppTheme
from .settings import AutoFormLayout, SettingsWrapper, SettingsAll, SettingsGroup, Setting

class Ui_Settings:
    def __init__(self):
        self.settingsWrapper: SettingsWrapper
        self.mainLayout: QVBoxLayout
        self.groupSettingsSelect: SettingsGrupSelector
        self.optionsPanel: QFrame
        self.buttonGroup: QSplitter
        self.closeButton: QPushButton
        self.saveButton: QPushButton
        self.optionsPanelLayout: AutoFormLayout
    
    def setupUi(self, dialog: QDialog):
        if not dialog.objectName():
            dialog.setObjectName("Dialog")
        dialog.resize(400, 200)
        dialog.setMinimumSize(QSize(400, 200))
        
        # INFO Add settings here
        defaultSettings = SettingsAll(
            [
                SettingsGroup("Appearance", [
                    Setting("Theme", AppTheme.default)
                ]),
                # SettingsGroup("Test setting group", [
                #     Setting("STRING", 'TAK')
                # ]),
            ] # TODO add grup with App settings that has: remove all saved templates, reset settings, ...
        )
        
        self.settingsWrapper = SettingsWrapper(defaultSettings)
        
        self.mainLayout = QVBoxLayout(dialog)
        self.mainLayout.setObjectName("mainLayout")
        
        self.optionsPanel = QFrame(dialog)
        self.optionsPanel.setObjectName("optionsPanel")
        optionsPanelSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.optionsPanel.setSizePolicy(optionsPanelSizePolicy)
        
        self.groupSettingsSelect = SettingsGrupSelector(self, dialog)
        self.groupSettingsSelect.setObjectName("groupSettingsSelect")
        optionsPanelSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.groupSettingsSelect.setSizePolicy(optionsPanelSizePolicy)
        self.mainLayout.addWidget(self.groupSettingsSelect)
        self.mainLayout.addWidget(self.optionsPanel)
        
        self.groupSettingsSelect.loadSettings()
        
        self.buttonGroup = QSplitter(dialog)
        self.buttonGroup.setOrientation(Qt.Orientation.Horizontal)
        self.buttonGroup.setObjectName("buttonGroup")
        self.mainLayout.addWidget(self.buttonGroup)
        
        self.closeButton = QPushButton("Close without saving", dialog)
        self.buttonGroup.addWidget(self.closeButton)
        self.closeButton.clicked.connect(lambda: self.closeWithoutSaving(dialog))
        
        self.saveButton = QPushButton("Save", dialog)
        self.saveButton.setObjectName("saveButton")
        self.buttonGroup.addWidget(self.saveButton)
        self.saveButton.clicked.connect(lambda: self.closeAndSave(dialog))
        
        # Save button custom style
        self.saveButton.setStyleSheet("* { background-color: darkgreen; color: white; } :disabled { background-color: transparent; }")
        
        # Larger text 
        self.groupSettingsSelect.setStyleSheet(
            """font-size: 16px;
            font-weight: bold;"""
        )

    def closeAndSave(self, dialog: QDialog):
        self.settingsWrapper.saveChangedSettings()
        dialog.accept()
    
    def closeWithoutSaving(self, dialog: QDialog):
        dialog.reject()

class SettingsGrupSelector(QComboBox):
    def __init__(self, ui: "Ui_Settings", /, parent: QWidget | None = None):
        super().__init__(parent)
        self.loadedSettings = ui.settingsWrapper.loadedSettings
        self.changedSettings = ui.settingsWrapper.changedSettings
        self.ui = ui
        ui.optionsPanelLayout = AutoFormLayout(self.loadedSettings, self.changedSettings, ui.optionsPanel)
        ui.optionsPanel.setLayout(ui.optionsPanelLayout)
    
    def loadSettings(self):
        if len(self.loadedSettings.groups) < 1:
            raise ValueError("Error loading settings, no groups found")
        if len(self.loadedSettings.groups) < 2:
            self.setDisabled(True)
        
        for group in self.loadedSettings.groups:
            self.addItem(group.name)
        
        self.loadGroupSettings(self.loadedSettings.groups[0])
        self.currentIndexChanged.connect(lambda _: self.changeDisplayedGroup(self.currentText()))
    
    def loadGroupSettings(self, settingsGroup: SettingsGroup):
        for setting in settingsGroup.items:
            self.ui.optionsPanelLayout.addRow(setting, settingsGroup.name)
            
    def changeDisplayedGroup(self, grupName: str):
        self.ui.optionsPanelLayout.clear()
        self.loadGroupSettings(self.loadedSettings[grupName])