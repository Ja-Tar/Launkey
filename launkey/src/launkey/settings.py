from enum import Enum
from typing import Any

from PySide6.QtCore import QSettings, Qt, QSize
from PySide6.QtGui import QPainter, QFocusEvent
from PySide6.QtWidgets import (
    QFormLayout, QWidget, QLineEdit, QSizePolicy,
    QComboBox, QLabel, 
)

from .theme_loader import AppTheme

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
    
    def __setitem__(self, name: str, toSetGroup: SettingsGroup):
        for settingsGroup in self.groups:
            if settingsGroup.name == name:
                settingsGroup.items = toSetGroup.items
                return
        self.groups.append(toSetGroup)

class SettingsWrapper(QSettings):
    def __init__(self, defaultSettings: SettingsAll):
        super().__init__("Ja-Tar", "Launkey")
        self.loadedSettings = self.loadSettings(defaultSettings)
        self.changedSettings: dict[str, Any] = {}
        
    def loadSettings(self, defaultSettings: SettingsAll) -> SettingsAll:
        allSettings = SettingsAll([])
        for settingsGroup in defaultSettings.groups:
            if len(settingsGroup.items) < 1:
                continue
            super().beginGroup(settingsGroup.name)
            for settingDefault in settingsGroup.items:
                settingType = self.getSavedType(settingDefault)
                settingDefault.item = settingDefault.itemType(
                    super().value(
                        settingDefault.name,
                        settingDefault.item,
                        settingType,
                    )
                )
                settingsGroup[settingDefault.name] = settingDefault
            super().endGroup()
            allSettings[settingsGroup.name] = settingsGroup

        return allSettings

    def getSavedType(self, settingDefault: Setting):
        # INFO Add more types as needed
        if isinstance(settingDefault.item, Enum):
            return type(settingDefault.item.value)
        elif isinstance(settingDefault.item, str):
            return str
        else:
            raise ValueError(f"No type found for setting: {settingDefault.name}")

    def saveChangedSettings(self):
        for settingsGroup in self.loadedSettings.groups:
            if len(settingsGroup.items) < 1:
                continue
            for setting in settingsGroup.items:
                address: str = settingsGroup.name + "/" + setting.name
                itemChanged = self.changedSettings.get(address, None)
                if itemChanged is not None and not setting.item == itemChanged:
                    print(f"setting changed: {setting.name}")
                    super().setValue(address, self.changedSettings[address])

class StringEditSetting(QLineEdit):
    def __init__(
        self,
        text: str,
        /,
        parent: QWidget | None = None
    ):
        super().__init__(text, parent)
        self.setObjectName("textSettingWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    
    def focusOutEvent(self, event: QFocusEvent) -> None:
        if event.reason() == Qt.FocusReason.OtherFocusReason:
            event.ignore()
            self.setModified(False)
            self.setFocus()
            return
        super().focusOutEvent(event)
        if self.isModified():
            self.editingFinished.emit()

class EnumEditSetting(QComboBox):
    def __init__(self, currentValue: Enum, /, parent: QWidget | None = None):
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
    def __init__(self, settings: SettingsAll, changedSettings: dict[str, Any], /, parent: QWidget | None = None):
        super().__init__(parent)
        self.setContentsMargins(20, 5, 20, 5)
        self.settings = settings
        self.changedSettings = changedSettings
        
    def getWidgetForType(self, setting: Setting, groupName: str) -> QWidget:
        # INFO Add more types as needed
        if isinstance(setting.item, Enum):
            widget = EnumEditSetting(setting.item)
            widget.currentIndexChanged.connect(lambda: self.setChangedSetting(groupName + "/" + setting.name, widget.currentIndex()))
            return widget
        elif isinstance(setting.item, str):
            widget = StringEditSetting(setting.item)
            widget.editingFinished.connect(lambda: self.setChangedSetting(groupName + "/" + setting.name, widget.text()))
            return widget
        else:
            raise NotImplementedError(f"Unsupported property type: {setting.itemType}")
        
    def setChangedSetting(self, settingLoc: str, item: Any):
        if not item in [AppTheme.magic, AppTheme.default]: # REMOVE after theme update
            self.changedSettings[settingLoc] = item
        
    def addRow(self, setting: Setting, groupName: str):
        super().addRow(CustomQLabel(setting.name + ": "), self.getWidgetForType(setting, groupName))

    def removeItem(self, itemName: str):
        for i in range(self.rowCount()):
            if self.itemAt(i, QFormLayout.ItemRole.LabelRole) is not None:
                label = self.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
                if isinstance(label, QLabel) and label.text() == itemName:
                    self.removeRow(i)
                    return
        raise ValueError(f"No item with name '{itemName}' found in layout.")
    
    def clear(self):
        for row in range(self.rowCount()):
            self.removeRow(row)
