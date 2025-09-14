from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QDialog
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence, QMouseEvent

from .templates import Template

class SquareButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None): 
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setMinimumSize(QSize(60, 60))

    def hasHeightForWidth(self) -> bool: # skipcq: PYL-R0201
        return True

    def heightForWidth(self, arg__1: int) -> int: # skipcq: PYL-R0201
        return arg__1

class PlusButton(SquareButton):
    def __init__(self, parent: QWidget | None = None):
        super().__init__("+", parent)
        self.setObjectName("plusButton")
        self.setMinimumSize(QSize(30, 30))
        self.setMaximumSize(QSize(50, 50))

class ToggleButton(SquareButton):
    def __init__(self, text: str, buttonID: str, parent: QWidget | None = None):
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

class QDialogNoDefault(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Cancel):
            self.reject()
        else:
            event.ignore()

class TemplateButton(SquareButton):
    def __init__(self, templateItems: list[Template | object], parent: QWidget | None = None):
        text = ""
        for item in templateItems:
            if isinstance(item, Template):
                text = item.name
                break
        if not text:
            raise ValueError("TemplateButton requires at least one Template with a name.")
        super().__init__(text, parent)

        self.setObjectName("templateButton")
        #self.setIconSize(QSize(64, 64))
        #self.setIcon(generatePreviewIcon(templateItems))
        # TODO add icon generation

        self.templateItems = templateItems

    def getTemplateItems(self) -> "list[Template | object]":
        return self.templateItems
