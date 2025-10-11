from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QDialog, QListWidget, QHBoxLayout, QSizePolicy,
    QWidget
)
#from PySide6.QtGui

from .theme_loader import AppTheme
from .settings import AutoFormLayout, AppSettings

class Ui_Settings:
    def setupUi(self, dialog: QDialog):
        if not dialog.objectName():
            dialog.setObjectName("Dialog")
        dialog.resize(600, 400)
        dialog.setMinimumSize(QSize(600, 400))
        
        self.mainLayout = QHBoxLayout(dialog)
        self.mainLayout.setObjectName("mainLayout")
        
        self.groupSettingsList = QListWidget(dialog)
        self.groupSettingsList.setObjectName("optionsPanel")
        optionsPanelSizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.groupSettingsList.setSizePolicy(optionsPanelSizePolicy)
        
        self.mainLayout.addWidget(self.groupSettingsList)
        
        self.optionsPanel = QWidget(dialog)
        self.optionsPanel.setObjectName("optionsPanel")
        optionsPanelSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.optionsPanel.setSizePolicy(optionsPanelSizePolicy)
        optionsPanelLayout = AutoFormLayout(self.optionsPanel)
        self.optionsPanel.setLayout(optionsPanelLayout)
        
        self.mainLayout.addWidget(self.optionsPanel)
        

        
        settings = AppSettings()
        
        allSettings = {
            "theme": {
                "set": settings.value("theme/set", AppTheme.normal, settingType=AppTheme),
            }
        }
        
        print(allSettings)
        
        
        
