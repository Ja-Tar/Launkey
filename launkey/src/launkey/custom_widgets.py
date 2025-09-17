from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QDialog, QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt, QSize, QRect, QPoint, QMimeData
from PySide6.QtGui import QKeySequence, QMouseEvent, QPixmap, QPainter, QDrag

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

        locationList = []
        for item in templateItems:
            if isinstance(item, TemplateItem):
                locationList.append(item.location)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.generateTemplatePreview(locationList)

    def generateTemplatePreview(self, locationList: list[tuple[int, int]]):
        # Example locationList: [(0,0), (1,1), (2,2)] (0,0) is center widget and (-1,-1) is top-left to it
        self.previewLabel = PreviewContainer(self)
        self.pixmap = self.generatePixmap(locationList)
        self.previewLabel.setPixmap(self.pixmap)
        layout = self.layout()
        if layout is not None:
            layout.addWidget(self.previewLabel)


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # TODO Move to two separate functions: one for generating pixmap for drag and one for displaying in label!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def generatePixmap(self, locationList: list[tuple[int, int]]) -> QPixmap:
        # Detect max size of the pixmap based on locations
        if not locationList:
            return QPixmap()

        min_row = min(loc[0] for loc in locationList)
        max_row = max(loc[0] for loc in locationList)
        min_col = min(loc[1] for loc in locationList)
        max_col = max(loc[1] for loc in locationList)
        rows = max_row - min_row + 1
        cols = max_col - min_col + 1
        cell_size = 30
        margin = 1
        space_between = 2
        pixmap_width = cols * cell_size + margin * 2
        pixmap_height = rows * cell_size + margin * 2
        pixmap = QPixmap(pixmap_width, pixmap_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for loc in locationList:
            row, col = loc
            x = (col - min_col) * cell_size + margin
            y = (row - min_row) * cell_size + margin
            rect = QRect(x, y, cell_size - space_between, cell_size - space_between)
            painter.fillRect(rect, Qt.GlobalColor.lightGray)
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
