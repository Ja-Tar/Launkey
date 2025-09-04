from enum import Enum
from typing import Any
from PySide6.QtWidgets import QWidget, QSizePolicy, QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon

from .templates import Template, LED

class StringEditWidget(QLineEdit):
    def __init__(self, text: str, property: str, objectToChange: object, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName("textEditWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.editingFinished.connect(lambda: self.changeObjectProperty(objectToChange, property, self.text()))

    def changeObjectProperty(self, objectToChange: object, property: str, newValue: Any):
        print(f"Changing string {property} to {newValue}")
        setattr(objectToChange, property, newValue)

class EnumEditWidget(QComboBox):
    def __init__(self, currentValue: Enum, property: str, objectToChange: object, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("enumEditWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        enumType = type(currentValue)
        for value in enumType:
            self.addItem(value.name, value)

        self.setCurrentText(currentValue.name)
        self.currentIndexChanged.connect(lambda _: self.changeObjectProperty(objectToChange, property, self.currentData()))

    def changeObjectProperty(self, objectToChange: object, property: str, newValue: Any):
        print(f"Changing enum {property} to {newValue}")
        setattr(objectToChange, property, newValue)

class ButtonColorSelector(QComboBox):
    def __init__(self, currentValue: tuple[int, int], property: str, objectToChange: object, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("buttonColorSelector")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(30)

        color_options = [
            ((LED.OFF, LED.OFF), "#cccccc"),
            ((LED.LOW, LED.OFF), "#ffcccc"),
            ((LED.MEDIUM, LED.OFF), "#ff8888"),
            ((LED.FULL, LED.OFF), "#ff0000"),
            ((LED.OFF, LED.LOW), "#ccffcc"),
            ((LED.OFF, LED.MEDIUM), "#88ff88"),
            ((LED.OFF, LED.FULL), "#00ff00"),
            ((LED.LOW, LED.LOW), "#ffffcc"),
            ((LED.MEDIUM, LED.MEDIUM), "#ffff88"),
            ((LED.FULL, LED.FULL), "#ffff00"),
            ((LED.MEDIUM, LED.LOW), "#ffd699"),
            ((LED.FULL, LED.MEDIUM), "#ffb366"),
            ((LED.FULL, LED.LOW), "#ff9900"),
            ((LED.LOW, LED.MEDIUM), "#ccff99"),
            ((LED.LOW, LED.FULL), "#99ff66"),
            ((LED.MEDIUM, LED.FULL), "#66ff33"),
        ]

        for value, color in color_options:
            pixmap = QPixmap(100, 20)
            pixmap.fill(QColor(color))
            icon = QIcon(pixmap)
            self.addItem(icon, "", value)
        self.setCurrentIndex(self.findData(currentValue))
        self.currentIndexChanged.connect(lambda _: self._changeObjectProperty(objectToChange, property, self.currentData()))

    def _changeObjectProperty(self, objectToChange: object, property: str, newValue: Any):
        print(f"Changing color {property} to {newValue}")
        setattr(objectToChange, property, newValue)

    def getColorValue(self) -> tuple[int, int]:
        return self.currentData()  # type: ignore

class TemplateOptionsList(QTreeWidget):
    def __init__(self, template_type: Template.Type, parent: QWidget | None = None):
        super().__init__(parent)
        optionsListPolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        optionsListPolicy.setHorizontalStretch(7)
        self.setSizePolicy(optionsListPolicy)
        self.setObjectName("optionsList")

        self.setHeaderLabels(["Option", "Value"])
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(True)

        self.loadDefaultOptions(template_type)

        self.template: Template

    def getWidgetForType(self, objectToChange: object, property: str, value: Any) -> QWidget:
        if isinstance(value, str):
            return StringEditWidget(value, property, objectToChange)
        elif isinstance(value, Enum):
            return EnumEditWidget(value, property, objectToChange)
        elif isinstance(value, tuple) and len(value) == 2 and all(isinstance(i, int) for i in value):
            return ButtonColorSelector(value, property, objectToChange)
        else:
            raise NotImplementedError(f"Unsupported property type: {type(value)}")

    def templateTypeOptions(self, template_type: Template) -> None:
        templateVars = vars(template_type)
        templateTopWidget = QTreeWidgetItem(["Template settings"], type=0)
        self.addTopLevelItem(templateTopWidget)

        for option, value in templateVars.items():
            widget = self.getWidgetForType(template_type, option, value)
            item = QTreeWidgetItem([option], type=1)
            templateTopWidget.addChild(item)
            self.setItemWidget(item, 1, widget)

    def loadDefaultOptions(self, template_type: Template.Type):
        # get options from template class
        self.clear()
        self.setStyleSheet(
            """
            QTreeView::item:selected {
            }

            QTreeView::item:hover {
            }

            QTreeView::item:hover:selected {
            }
            """
        )

        self.template = Template(name="Example", type=template_type)
        self.templateTypeOptions(self.template)
        self.expandAll()
        self.resizeColumnToContents(0)
        self.header().setStretchLastSection(True)
    
    def getObjects(self) -> list[object]:
        return [self.template]
