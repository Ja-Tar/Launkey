from enum import Enum
from typing import Any
from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QSizePolicy, QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon

from .templates import Template

class SquareButton(QPushButton):
    def __init__(self, text: str, parent: QWidget = None): # type: ignore
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setMinimumSize(QSize(60, 60))

    def hasHeightForWidth(self) -> bool: # skipcq: PYL-R0201
        return True

    def heightForWidth(self, arg__1: int) -> int: # skipcq: PYL-R0201
        return arg__1

class PlusButton(SquareButton):
    def __init__(self, parent: QWidget = None): # type: ignore
        super().__init__("+", parent)
        self.setObjectName("plusButton")
        self.setMinimumSize(QSize(30, 30))
        self.setMaximumSize(QSize(50, 50))

class ToggleButton(SquareButton):
    def __init__(self, text: str, buttonID: str, parent: QWidget = None): # type: ignore
        super().__init__(text, parent)
        self.setObjectName("toggleButton")
        self.setCheckable(True)
        self.setChecked(False)
        self.setStyleSheet("border-color: darkgray; border-width: 1px;")
        self.toggled.connect(self.onToggled)

        self.buttonID = buttonID

    def onToggled(self, checked: bool):
        self.setStyleSheet("border: 5px solid lightblue; border-width: 5px;" if checked else "border-color: darkgray; border-width: 1px;")

    def getButtonID(self) -> str:
        return self.buttonID

    def checkToggle(self, buttonID: str):
        if self.buttonID != buttonID:
            self.setChecked(False)
        else:
            self.setChecked(True)

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
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("buttonColorSelector")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(30)

        color_options = [
            ((0, 0), "#cccccc"),
            ((1, 0), "#ffcccc"),
            ((2, 0), "#ff8888"),
            ((3, 0), "#ff0000"),
            ((0, 1), "#ccffcc"),
            ((0, 2), "#88ff88"),
            ((0, 3), "#00ff00"),
            ((1, 1), "#ffffcc"),
            ((2, 2), "#ffff88"),
            ((3, 3), "#ffff00"),
            ((2, 1), "#ffd699"),
            ((3, 2), "#ffb366"),
            ((3, 1), "#ff9900"),
            ((1, 2), "#ccff99"),
            ((1, 3), "#99ff66"),
            ((2, 3), "#66ff33"),
        ]
        for value, color in color_options:
            self.addItem("", value)
            idx = self.count() - 1
            self.setItemData(idx, color, Qt.ItemDataRole.BackgroundRole)
            # Set a colored icon as well for better visibility
            pixmap = QPixmap(20, 20)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QColor(color))
            painter.setPen(Qt.GlobalColor.transparent)
            painter.drawRect(0, 0, 20, 20)
            painter.end()
            self.setItemIcon(idx, QIcon(pixmap))

    def getColorValue(self) -> tuple[int, int]:
        return self.currentData()  # type: ignore

class TemplateOptionsList(QTreeWidget):
    def __init__(self, parent: QWidget | None = None):
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

        self.loadDefaultOptions(Template.Type.BUTTONS)

        self.template: Template

    def getWidgetForType(self, objectToChange: object, property: str, value: Any) -> QWidget:

        if isinstance(value, str):
            return StringEditWidget(value, property, objectToChange)
        elif isinstance(value, Enum):
            return EnumEditWidget(value, property, objectToChange)
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
