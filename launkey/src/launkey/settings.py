from enum import Enum
from typing import Any

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QFormLayout, QWidget, QLineEdit, QSizePolicy,
    QComboBox, QLabel
)

class AppSettings(QSettings):
    def __init__(self):
        super().__init__("Ja-Tar", "Launkey")
        
    def value(self, settingKey: str, settingDefault: Any = None, settingType: type | None = None) -> Any:
        if isinstance(settingDefault, Enum):
            enumType = type(settingDefault)
            rawValue = super().value(settingKey, settingDefault.name, str)
            try:
                return enumType[rawValue] # type: ignore
            except KeyError:
                return settingDefault
        
        return super().value(settingKey, settingDefault, settingType)
    
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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
    def __init__(self, /, parent: QWidget):
        super().__init__(parent)
        
    def getWidgetForType(self, value: Any) -> QWidget:
        if isinstance(value, Enum):
            return EnumEditSetting(value)
        elif isinstance(value, str):
            return StringEditSetting(value)
        else:
            raise NotImplementedError(f"Unsupported property type: {type(value)}")
        
    def addItem(self, itemName: str, itemClass: object):
        super().addRow(QLabel(itemName), self.getWidgetForType(itemClass))

    def removeItem(self, itemName: str):
        for i in range(self.rowCount()):
            if self.itemAt(i, QFormLayout.ItemRole.LabelRole) is not None:
                label = self.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
                if isinstance(label, QLabel) and label.text() == itemName:
                    self.removeRow(i)
                    return
        raise ValueError(f"No item with name '{itemName}' found in layout.")
        