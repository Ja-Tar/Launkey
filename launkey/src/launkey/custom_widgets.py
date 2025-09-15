from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QDialog, QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence

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

class TemplateDisplay(QFrame):
    def __init__(self, templateItems: list[Template | object], parent: QWidget | None = None):
        super().__init__(parent)
        self.text = ""
        for item in templateItems:
            if isinstance(item, Template):
                self.text = item.name
                break
        if not self.text:
            raise ValueError("TemplateDisplay requires at least one Template with a name.")
        self.templateItems = templateItems
        self.setObjectName("templateDisplay")
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setMinimumSize(QSize(60, 60))
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Plain)

        # TODO Add widget to display Template preview and that can be dragged to Launchpad Table
        self.preview = QFrame(self)
        self.preview.setObjectName("templatePreview")
        previewSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.preview.setSizePolicy(previewSizePolicy)
        self.preview.setFrameShape(QFrame.Shape.Panel)
        self.preview.setFrameShadow(QFrame.Shadow.Raised)
        self.preview.setLineWidth(2)
        self.generateTemplatePreview()

        self.label = QLabel(self.text, self)
        labelSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.label.setSizePolicy(labelSizePolicy)
        self.label.setObjectName("templateLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.preview)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def hasHeightForWidth(self) -> bool: # skipcq: PYL-R0201
        return True

    def heightForWidth(self, arg__1: int) -> int: # skipcq: PYL-R0201
        return arg__1

    def getTemplateItems(self) -> "list[Template | object]":
        return self.templateItems
    
    def generateTemplatePreview(self):
        # TODO Implement preview generation based on Template data
        pass