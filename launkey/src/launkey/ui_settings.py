from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QDialog, QComboBox, QVBoxLayout, QSizePolicy,
    QFrame, QSplitter, QPushButton
)
#from PySide6.QtGui

from .theme_loader import AppTheme
from .settings import AutoFormLayout, AppSettings

class Ui_Settings:
    def setupUi(self, dialog: QDialog):
        if not dialog.objectName():
            dialog.setObjectName("Dialog")
        dialog.resize(400, 200)
        dialog.setMinimumSize(QSize(400, 200))
        
        self.mainLayout = QVBoxLayout(dialog)
        self.mainLayout.setObjectName("mainLayout")
        
        self.groupSettingsSelect = QComboBox(dialog)
        self.groupSettingsSelect.setObjectName("groupSettingsSelect")
        optionsPanelSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.groupSettingsSelect.setSizePolicy(optionsPanelSizePolicy)
        self.mainLayout.addWidget(self.groupSettingsSelect)
        
        self.optionsPanel = QFrame(dialog)
        self.optionsPanel.setObjectName("optionsPanel")
        optionsPanelSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.optionsPanel.setSizePolicy(optionsPanelSizePolicy)
        self.optionsPanelLayout = AutoFormLayout(self.optionsPanel)
        self.optionsPanel.setLayout(self.optionsPanelLayout)
        self.mainLayout.addWidget(self.optionsPanel)
        
        self.buttonGroup = QSplitter(dialog)
        self.buttonGroup.setOrientation(Qt.Orientation.Horizontal)
        self.buttonGroup.setObjectName("buttonGroup")
        self.mainLayout.addWidget(self.buttonGroup)
        
        self.closeButton = QPushButton("Close without saving", dialog)
        self.buttonGroup.addWidget(self.closeButton)
        self.closeButton.clicked.connect(lambda: self.closeWithoutSaving(dialog))
        
        self.saveButton = QPushButton("Save", dialog)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setDefault(True)
        self.buttonGroup.addWidget(self.saveButton)
        self.saveButton.clicked.connect(lambda: self.closeAndSave(dialog))
        
        # Save button custom style
        self.saveButton.setStyleSheet("* { background-color: darkgreen; color: white; } :disabled { background-color: transparent; }")
        
        # Larger text 
        self.groupSettingsSelect.setStyleSheet(
            """font-size: 16px;
            font-weight: bold;"""
        )
        
        # INFO Add settings here
        defaultSettings = {
            "Appearance": {
                "Theme: ": AppTheme.system,
            },
            "Test setting group": {
                "oki": "Oki"
            } # TODO add grup with App settings that has: remove all saved templates, reset settings, ...
        }
        
        self.settings = AppSettings()
        self.allSettings = settingsClass.getAllSettings(defaultSettings)
        
        self.loadSettings()

    def loadSettings(self):        
        groupName = self.loadGroupSelection()
        
        currentSettingGroup = self.allSettings[groupName]
        for settingName in currentSettingGroup:
            self.optionsPanelLayout.addRow(settingName, currentSettingGroup[settingName])

    def loadGroupSelection(self) -> str:
        for settingGroup in self.allSettings:
            self.groupSettingsSelect.addItem(settingGroup)
            
        if len(self.allSettings) < 1:
            raise ValueError("Error loading settings, no groups found")
        if len(self.allSettings) < 2:
            self.groupSettingsSelect.setDisabled(True)
            
        self.groupSettingsSelect.setCurrentIndex(0)
        return next(iter(self.allSettings))

    def closeAndSave(self, dialog: QDialog):
        #self.settings.saveChangedSettings()
        dialog.accept()
    
    def closeWithoutSaving(self, dialog: QDialog):
        dialog.reject()
        
        
        
        
        
        
            
        
        
        
