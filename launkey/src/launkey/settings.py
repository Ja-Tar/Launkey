from enum import Enum
from typing import Any

from PySide6.QtCore import QSettings, Qt, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QFormLayout, QWidget, QLineEdit, QSizePolicy,
    QComboBox, QLabel
)

#from .template_options_widgets import StringEditWidget

class AppSettings(QSettings):
    def __init__(self):
        super().__init__("Ja-Tar", "Launkey")
        self.loadedSettings: dict[str, dict[str, object]] = {}

    def getAllSettings(
        self, defaultSettings: dict[str, dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        allSettings: dict[str, dict[str, Any]] = {}
        for settingsGroupName in defaultSettings:
            settingsGroup = defaultSettings[settingsGroupName]
            allSettingsGroup: dict[str, object] = {}
            if len(settingsGroup) < 1:
                continue
            super().beginGroup(settingsGroupName)
            for settingName in settingsGroup:
                settingDefault = settingsGroup[settingName]
                settingType, savedType = self.getSettingType(settingName, settingDefault)
                settingValue = settingType(super().value(settingName, settingDefault, savedType))
                allSettingsGroup[settingName] = settingValue
            super().endGroup()
            allSettings[settingsGroupName] = allSettingsGroup

        self.loadedSettings = allSettings
        return allSettings

    def getSettingType(
        self, settingName, settingDefault
    ) -> tuple[type[Enum], type[int]] | tuple[type[str], type[str]]:
        # INFO Add more types as needed
        if isinstance(settingDefault, Enum):
            return settingDefault.__class__, type(settingDefault.value)
        elif isinstance(settingDefault, str):
            return str, str
        else:
            raise ValueError(f"No type found for setting: {settingName}")

    def saveChangedSettings(self, changedSettings: dict[str, dict[str, Any]]):
        for settingsGroupName in changedSettings:
            settingsGroup = changedSettings[settingsGroupName]
            oldSettingsGroup = self.loadedSettings[settingsGroupName]
            if len(oldSettingsGroup) < 1:
                continue
            super().beginGroup(settingsGroupName)
            for settingName in settingsGroup:
                if self.settingChanged(settingsGroup[settingName], oldSettingsGroup[settingName]):
                    print(f"setting changed: {settingName}")
                    super().setValue(settingName, settingsGroup[settingName])
            super().endGroup()
    
    @staticmethod
    def settingChanged(new, old):
        return new == old

class StringEditSetting(QLineEdit):
    def __init__(
        self,
        text: str,
        parent: QWidget | None = None
    ):
        super().__init__(text, parent)
        self.setObjectName("textSettingWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

class EnumEditSetting(QComboBox):
    def __init__(self, currentValue: Enum, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("enumEditWidget")

        enumType = type(currentValue)
        for value in enumType:
            self.addItem(value.name, value)
        
        if self.count() <= 0:
            self.setDisabled(True)
            raise ValueError(f"No enum values found for {enumType}")
        elif self.count() == 1:
            self.setDisabled(True)

        self.setCurrentText(currentValue.name)

class CustomQLabel(QLabel):
    def __init__(self, text: str, /, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setStyleSheet(
            """font-size: 14px;"""
        )

class AutoFormLayout(QFormLayout):
    def __init__(self, /, parent: QWidget | None = None):
        super().__init__(parent)
        self.setContentsMargins(20, 5, 20, 5)
        
    def getWidgetForType(self, value: Any) -> QWidget:
        if isinstance(value, Enum):
            return EnumEditSetting(value)
        elif isinstance(value, str):
            return StringEditSetting(value)
        else:
            raise NotImplementedError(f"Unsupported property type: {type(value)}")
        
    def addRow(self, itemName: str, itemClass: object):
        super().addRow(CustomQLabel(itemName), self.getWidgetForType(itemClass))

    def removeItem(self, itemName: str):
        for i in range(self.rowCount()):
            if self.itemAt(i, QFormLayout.ItemRole.LabelRole) is not None:
                label = self.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
                if isinstance(label, QLabel) and label.text() == itemName:
                    self.removeRow(i)
                    return
        raise ValueError(f"No item with name '{itemName}' found in layout.")
