from enum import Enum
from typing import Any

from PySide6.QtCore import QSettings, Qt, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QFormLayout, QWidget, QLineEdit, QSizePolicy,
    QComboBox, QLabel
)

from .template_options_widgets import StringEditWidget

class CustomQLabel(QLabel):
    def __init__(self, text: str, /, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setStyleSheet(
            """font-size: 14px;"""
        )

class Setting():
    def __init__(self, name: str, item: Enum | str):
        self.name = name
        self.itemType = type(item)
        self.item = item
        
    def getQLabel(self) -> CustomQLabel:
        return CustomQLabel(self.name)

class SettingsGroup():
    def __init__(self, name: str, items: list[Setting]):
        self.name = name
        self.items = items
        
    def __getitem__(self, name: str) -> Setting:
        for setting in self.items:
            if setting.name == name:
                return setting
        raise KeyError(f"No setting with name '{name}' found in group '{self.name}'")
    
    def __setitem__(self, name: str, value: Setting):
        for setting in self.items:
            if setting.name == name:
                setting = value
                return
        self.items.append(value)

class SettingsAll():
    def __init__(self, groups: list[SettingsGroup]):
        self.groups = groups
    
    def __getitem__(self, name: str) -> SettingsGroup:
        for group in self.groups:
            if group.name == name:
                return group
        raise KeyError(f"No group with name '{name}' found!")
    
    def __setitem__(self, name: str, value: list[Setting]):
        for settingsGroup in self.groups:
            if settingsGroup.name == name:
                settingsGroup.items = value
                return
        self.groups.append(SettingsGroup(name, value))

class SettingsWrapper(QSettings):
    def __init__(self, defaultSettings: SettingsAll):
        super().__init__("Ja-Tar", "Launkey")
        self.loadedSettings = self.loadSettings(defaultSettings)
        self.currentSettings = SettingsAll([])

    def loadSettings(self, defaultSettings: SettingsAll) -> SettingsAll:
        allSettings = SettingsAll([])
        for settingsGroup in defaultSettings.groups:
            if len(settingsGroup.items) < 1:
                continue
            super().beginGroup(settingsGroup.name)
            for settingDefault in settingsGroup.items:
                settingDefault.item = settingDefault.itemType(
                    super().value(
                        settingDefault.name,
                        settingDefault.item,
                        self.getSavedType(settingDefault),
                    )
                )
                settingsGroup[settingDefault.name] = settingDefault
            super().endGroup()
            allSettings[settingsGroup.name] = settingsGroup.items

        return allSettings

    def getSavedType(self, settingDefault: Setting) -> type[Any]:
        # INFO Add more types as needed
        if isinstance(settingDefault.item, Enum):
            return type(settingDefault.item.value)
        elif isinstance(settingDefault.item, str):
            return str
        else:
            raise ValueError(f"No type found for setting: {settingDefault.name}")

    def saveChangedSettings(self):
        for settingsGroup in self.currentSettings.groups:
            oldSettingsGroup = self.loadedSettings[settingsGroup.name]
            if len(oldSettingsGroup.items) < 1:
                continue
            super().beginGroup(settingsGroup.name)
            for setting in settingsGroup.items:
                if self.settingChanged(setting.item, oldSettingsGroup[setting.name]):
                    print(f"setting changed: {setting.name}")
                    super().setValue(setting.name, setting.item)
            super().endGroup()

    @staticmethod
    def settingChanged(new, old):
        return new == old

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

class AutoFormLayout(QFormLayout):
    def __init__(self, settings: SettingsAll, /, parent: QWidget | None = None):
        super().__init__(parent)
        self.setContentsMargins(20, 5, 20, 5)
        self.settings = settings
        
    def getWidgetForType(self, setting: Setting) -> QWidget:
        if isinstance(setting.item, Enum):
            return EnumEditSetting(setting.item)
        elif isinstance(setting.item, str):
            return StringEditWidget(setting.item, setting.item, setting)
        else:
            raise NotImplementedError(f"Unsupported property type: {setting.itemType}")
        
    def addRow(self, setting: Setting):
        super().addRow(CustomQLabel(setting.name), self.getWidgetForType(setting))

    def removeItem(self, itemName: str):
        for i in range(self.rowCount()):
            if self.itemAt(i, QFormLayout.ItemRole.LabelRole) is not None:
                label = self.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
                if isinstance(label, QLabel) and label.text() == itemName:
                    self.removeRow(i)
                    return
        raise ValueError(f"No item with name '{itemName}' found in layout.")
