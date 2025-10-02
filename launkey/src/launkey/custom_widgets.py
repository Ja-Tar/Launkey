import time
import struct

from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget, QPushButton, QSizePolicy,
    QDialog, QLabel, QFrame, QVBoxLayout,
    QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QSize, QRect, QMimeData, QPoint
from PySide6.QtGui import (
    QCloseEvent, QKeySequence, QMouseEvent, 
    QPixmap, QPainter, QDrag, QResizeEvent, 
    QLinearGradient, QColor
)

from .templates import Template, TemplateItem, Button, sterilizeTemplateName, ledsToColorCode

if TYPE_CHECKING:
    from .mainwindow import Launkey

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
        self.setStyleSheet("border: 5px solid lightblue;" if checked else "border-color: darkgray; border-width: 1px;")

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

class QAutoStatusBar(QStatusBar):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setSizeGripEnabled(False)

    def removeWidget(self, widget: QWidget) -> None:
        super().removeWidget(widget)
        widget.deleteLater()

    def deleteByText(self, name: str):
        for widget in self.findChildren(QLabelInfo):
            if widget.text() == name:
                self.removeWidget(widget)
                break

class QLabelInfo(QLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None, /, colour: str | None = None):
        super().__init__(text, parent)
        self.setObjectName("statusBarInfo")
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.setContentsMargins(10, 0, 10, 0)
        if colour:
            self.setStyleSheet(f"color: {colour}; font-weight: bold;")

class ShortcutDisplay(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Test Mode - Shortcut Tester")
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(400, 100)

        self.label = QLabel("", self)
        self.label.setObjectName("shortcutLabel")
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        self.label.setMinimumSize(QSize(200, 50))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sideLabel = QLabel("Top Half", self)
        self.sideLabel.setObjectName("sideLabel")
        self.sideLabel.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self.sideLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.sideLabel)
        self.setLayout(layout)

        self.closeEvent = self.onXButtonClick

        self.pressedShortcuts: list[str] = []

    def dynamicFontSize(self):
        font = self.label.font()
        fontSize = 48
        font.setPointSize(fontSize)
        self.label.setFont(font)
        while self.label.fontMetrics().horizontalAdvance(self.label.text()) > self.label.width() - 20 and fontSize > 1:
            fontSize -= 1
            font.setPointSize(fontSize)
            self.label.setFont(font)

    def showShortcuts(self):
        if not self.pressedShortcuts:
            self.label.setText("")
        else:
            self.label.setText("; ".join(self.pressedShortcuts))
        self.dynamicFontSize()
    
    def setShortcutText(self, text: str):
        if text not in self.pressedShortcuts:
            self.pressedShortcuts.append(text)
        self.showShortcuts()

    def clearShortcutText(self, text: str):
        if text in self.pressedShortcuts:
            self.pressedShortcuts.remove(text)
        self.showShortcuts()

    def changeSideLabel(self, text: str):
        self.sideLabel.setText(text)
    
    def onXButtonClick(self, event: QCloseEvent):
        event.ignore()

class AreYouSureDialog(QMessageBox):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Icon.Warning)
        self.setWindowTitle("Close without saving?")
        self.setText(text)
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.setDefaultButton(QMessageBox.StandardButton.No)
        self.setEscapeButton(QMessageBox.StandardButton.No)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

class TemplateDisplay(QFrame):
    def __init__(self, main_window: "Launkey", templateItems: list[Template | TemplateItem], parent: QWidget | None = None):
        super().__init__(parent)
        self.main_window = main_window
        self.text = ""
        for item in templateItems:
            if isinstance(item, Template):
                self.text = item.name
                break
        if not self.text:
            raise ValueError("TemplateDisplay requires at least one Template with a name.")
        self.templateFileName = sterilizeTemplateName(self.text)
        self.templateItems = templateItems
        self.setObjectName(f"templateDisplay-{self.templateFileName}")
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setMinimumSize(QSize(60, 60))
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Plain)

        self.preview = Preview(self.templateFileName, self.templateItems, self)

        self.label = QLabel(self.text, self)
        labelSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.label.setSizePolicy(labelSizePolicy)
        self.label.setObjectName("templateLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.preview)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            from .mainwindow import editTemplatePopup
            editTemplatePopup(self.main_window, self.text)
        super().mousePressEvent(event)

    def hasHeightForWidth(self) -> bool: # skipcq: PYL-R0201
        return True

    def heightForWidth(self, arg__1: int) -> int: # skipcq: PYL-R0201
        return arg__1

    def getTemplateItems(self) -> list[Template | TemplateItem]:
        return self.templateItems

class Preview(QFrame):
    def __init__(self, fileName: str, templateItems: list[Template | TemplateItem], parent: QWidget | None = None):
        super().__init__(parent)
        self.templateName = fileName

        self.setObjectName(f"templatePreview-{self.templateName}")
        previewSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        self.setSizePolicy(previewSizePolicy)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)

        self.locationList: list[tuple[int, int]] = []
        self.normalColorList: list[str] = []
        self.pushedColorList: list[str] = []
        for item in templateItems:
            if isinstance(item, TemplateItem):
                self.locationList.append(item.location)
                # TODO Add more types of TemplateItem when more are added
                if isinstance(item, Button): # Only Button has colors for now
                    self.normalColorList.append(ledsToColorCode(item.normalColor))
                    self.pushedColorList.append(ledsToColorCode(item.pushedColor))


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
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.dragPixmap = self.generatePixmap(self.locationList)

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.called + 0.05 < time.time(): # Resize throttling - only update every 50 ms
            self.called = time.time()
            self.displayPixmap = self.generatePixmap(self.locationList, self.size() - QSize(4, 4), space_between=4, padding=2, drawCustomBackground=True)
            self.previewLabel.setPixmap(self.displayPixmap)
        super().resizeEvent(event)

    def generatePixmap(
        self,
        locationList: list[tuple[int, int]],
        maxSize: QSize | None = None,
        /,
        drawCustomBackground: bool = False,
        padding: int = 4,
        space_between: int = 2,
        min_cell_size: int = 1,
        max_cell_size: int = 40,
        default_cell_size: int = 36,
        default_space_between: int = 4
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
        else:
            space_between = default_space_between

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
            index = locationList.index((row, col))
            if not drawCustomBackground:
                # Draw border
                painter.setBrush(QColor("#888888"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect, 7, 7)

                # Fill inner cell
                rect.adjust(2, 2, -2, -2)  # Smaller rect for inner fill
                painter.setBrush(QColor("#555555"))
                painter.drawRoundedRect(rect, 5, 5)
                continue
            normal_color = self.normalColorList[index] if index < len(self.normalColorList) else Qt.GlobalColor.lightGray
            pushed_color = self.pushedColorList[index] if index < len(self.pushedColorList) else Qt.GlobalColor.lightGray

            # One half is normal color and the other has pushed color
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, QColor(normal_color))
            gradient.setColorAt(0.51, QColor(normal_color))
            gradient.setColorAt(0.52, QColor(pushed_color))
            gradient.setColorAt(1, QColor(pushed_color))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 5, 5)

            # Draw a semicircle at the middle point and facing to the bottom right
            painter.setBrush(QColor("#555555"))
            painter.setPen(Qt.PenStyle.NoPen)
            radius = cell_size // 4
            center_x = x + cell_size // 2
            center_y = y + cell_size // 2
            rect = QRect(center_x - radius, center_y - radius, 2 * radius, 2 * radius)
            start_angle = 225 * 16  # 225 degrees
            span_angle = 180 * 16  # 180 degrees
            painter.drawArc(rect, start_angle, span_angle)
            painter.drawPie(rect, start_angle, span_angle)

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

        mimeData.setText(self.templateName)  # Template file name as text
        # Convert locationList (list of tuples) to bytes for MIME data
        # Flatten the list of (row, col) tuples to a bytes object
        loc_bytes = b''.join(struct.pack('ii', row, col) for row, col in self.locationList)
        mimeData.setData("application/x-template", loc_bytes)  # Custom MIME type with occupied positions
        drag.setMimeData(mimeData)
        
        pixmap = self.dragPixmap
        drag.setPixmap(pixmap)
        # Find the (0, 0) location and set hotspot to its center if present, else use pixmap center
        self.getDragHotspot(pixmap)
        drag.setHotSpot(self.getDragHotspot(pixmap))
        drag.setObjectName(f"drag-{self.templateName}")

        drag.exec(Qt.DropAction.CopyAction)

    def getDragHotspot(self, pixmap: QPixmap) -> QPoint:
        if (0, 0) in self.locationList:
            # Calculate grid bounds
            min_row = min(row for row, _ in self.locationList)
            min_col = min(col for _, col in self.locationList)
            
            # Layout parameters
            cell_size = 36  # Use default_cell_size
            space_between = 4
            padding = 2
            x = padding + (0 - min_col) * (cell_size + space_between) + cell_size // 2
            y = padding + (0 - min_row) * (cell_size + space_between) + cell_size // 2
            return QPoint(x, y)
        else:
            return pixmap.rect().center()
