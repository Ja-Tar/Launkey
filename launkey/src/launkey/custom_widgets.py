from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QDialog, QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt, QSize, QRect, QPoint, QMimeData
from PySide6.QtGui import QKeySequence, QMouseEvent, QPixmap, QPainter, QDrag

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
        self.preview = Preview(self)

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

class Preview(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("templatePreview")
        previewSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.setSizePolicy(previewSizePolicy)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.generateTemplatePreview()

    def generatePixmap(self) -> QPixmap:
        pixmapSize = QSize(50, 50)
        pixmap = QPixmap(pixmapSize)
        painter = QPainter(pixmap)

        painter.fillRect(QRect(QPoint(0, 0), pixmapSize), Qt.GlobalColor.red)

        # TODO Draw template preview content onto the pixmap

        painter.end()
        return pixmap

    def generateTemplatePreview(self):
        self.previewLabel = PreviewContainer(self)

        # TODO Implement preview generation based on Template data (with size fitting)

        self.pixmap = self.generatePixmap()
        self.previewLabel.setPixmap(self.pixmap)
        layout = self.layout()
        if layout is not None:
            layout.addWidget(self.previewLabel)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QMouseEvent(event)
            drag.setAccepted(True)
            self.startDrag()
        super().mousePressEvent(event)
    
    def startDrag(self):
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText("templateDrag")
        drag.setMimeData(mimeData)

        pixmap = self.pixmap
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())

        drag.exec(Qt.DropAction.CopyAction)

class PreviewContainer(QLabel):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("templatePreviewContainer")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        if self.pixmap():
            self.setPixmap(self.pixmap().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def setPixmap(self, pixmap):
        super().setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
