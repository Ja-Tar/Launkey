import time

from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QDialog, QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt, QSize, QRect, QMimeData
from PySide6.QtGui import QKeySequence, QMouseEvent, QPixmap, QPainter, QDrag, QResizeEvent

from .templates import Template, TemplateItem

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
    def __init__(self, templateItems: list[Template | TemplateItem], parent: QWidget | None = None):
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
        self.preview = Preview(self.templateItems, self)

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

    def getTemplateItems(self) -> list[Template | TemplateItem]:
        return self.templateItems

class Preview(QFrame):
    def __init__(self, templateItems: list[Template | TemplateItem], parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("templatePreview")
        previewSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.setSizePolicy(previewSizePolicy)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)

        self.locationList = []
        for item in templateItems:
            if isinstance(item, TemplateItem):
                self.locationList.append(item.location)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.previewLabel = QLabel(self)
        self.previewLabel.setObjectName("previewLabel")
        self.previewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.previewLabel.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.previewLabel)

        self.dragPixmap: QPixmap
        self.displayPixmap: QPixmap
        self.called = 0.0

        self.setupDrag()

    def setupDrag(self):
        self.setAcceptDrops(True)
        self.previewLabel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.dragPixmap = self.generatePixmap(self.locationList)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.called + 0.05 < time.time(): # Resize throttling - only update every 50 ms
            self.called = time.time()
            self.displayPixmap = self.generatePixmap(self.locationList, self.size() - QSize(4, 4), space_between=4, padding=2)
            self.previewLabel.setPixmap(self.displayPixmap)
        super().resizeEvent(event)

    def generatePixmap(
        self,
        locationList: list[tuple[int, int]],
        maxSize: QSize | None = None,
        /,
        padding: int = 4,
        space_between: int = 2,
        min_cell_size: int = 1,
        max_cell_size: int = 40,
        default_cell_size: int = 28
    ) -> QPixmap:
        if not locationList:
            return QPixmap()

        # Calculate grid bounds
        min_row = min(row for row, _ in locationList)
        max_row = max(row for row, _ in locationList)
        min_col = min(col for _, col in locationList)
        max_col = max(col for _, col in locationList)
        rows = max_row - min_row + 1
        cols = max_col - min_col + 1

        # Layout parameters
        cell_size = default_cell_size # Default cell size
        if maxSize is not None:
            cell_size = min(
            max((maxSize.width() - 2 * padding - (cols - 1) * space_between) // cols, min_cell_size),
            max((maxSize.height() - 2 * padding - (rows - 1) * space_between) // rows, min_cell_size),
            max_cell_size
            )

        pixmap_width = cols * cell_size + (cols - 1) * space_between + 2 * padding
        pixmap_height = rows * cell_size + (rows - 1) * space_between + 2 * padding
        pixmap = QPixmap(pixmap_width, pixmap_height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for row, col in locationList:
            x = padding + (col - min_col) * (cell_size + space_between)
            y = padding + (row - min_row) * (cell_size + space_between)
            rect = QRect(x, y, cell_size, cell_size)
            painter.fillRect(rect, Qt.GlobalColor.lightGray)
            painter.setPen(Qt.GlobalColor.darkGray)
            painter.drawRect(rect)

        painter.end()
        return pixmap

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QMouseEvent(event)
            drag.setAccepted(True)
            self.startDrag()
        super().mousePressEvent(event)

    def startDrag(self):
        drag = QDrag(self)
        # TODO: Set data to identify the template being dragged
        mimeData = QMimeData()
        mimeData.setText("templateDrag")
        drag.setMimeData(mimeData)

        pixmap = self.dragPixmap
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())

        drag.exec(Qt.DropAction.CopyAction)
