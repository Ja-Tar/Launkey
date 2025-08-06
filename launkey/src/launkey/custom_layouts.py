from PySide6.QtWidgets import QGridLayout
from PySide6.QtCore import Qt

# From https://github.com/chinmaykrishnroy/PyQt5DynamicFlowLayout
class DynamicGridLayout(QGridLayout):
    def __init__(self, parent=None, min_col_width=360, min_row_height=116):
        super().__init__(parent)
        self.min_col_width = min_col_width
        self.min_row_height = min_row_height
        self.items = []
        self.num_cols = 0
        # Dodaj filtr zdarzeń do rodzica, jeśli istnieje
        if parent is not None:
            parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj is self.parentWidget() and event.type() == QEvent.Resize:
            self.update_layout()
        return super().eventFilter(obj, event)

    def addWidget(self, widget, rowSpan=1, colSpan=1, alignment=None):
        item = (widget, rowSpan, colSpan, alignment)
        self.items.append(item)
        super().addWidget(widget, 0, 0, rowSpan, colSpan)
        self.update_layout()

    def update_layout(self):
        if not self.parentWidget():
            return

        width = self.parentWidget().width()
        new_num_cols = max(1, width // self.min_col_width)
        item_width = width // new_num_cols

        if new_num_cols != self.num_cols:
            self.num_cols = new_num_cols

        row = col = 0
        for widget, rowSpan, colSpan, alignment in self.items:
            widget.setFixedHeight(item_width * self.min_row_height // self.min_col_width)
            super().addWidget(widget, row, col, rowSpan, colSpan)
            col += 1
            if col >= self.num_cols:
                col = 0
                row += 1

class CenterGridLayout(QGridLayout):
    """
    A layout that aligns widgets in a centered grid
    with one item in the middle that is always centered,
    other items aligned around it, and plus buttons on the edges.
    Rows and columns are automatically determined based on the number of items.
    """
    def __init__(self, parent=None, mainWidget=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.rows = 3
        self.cols = 3
        self.mainItem = mainWidget  # central widget, x and y is (0, 0)
        # x and y are relative to the main item
        self.otherItems = []  # (widget, x, y)
        self.plusButtons = [] # (widget, x, y)

    def addWidget(self, widget, x, y):
        """Dodaje widget na określonej pozycji."""
        if x == 0 and y == 0:
            self.mainItem = widget
        else:
            self.otherItems.append((widget, x, y))
        self.update_layout()

    def clear(self):
        self.otherItems = []
        self.plusButtons = []
        self.update_layout()

    def update_layout(self):
        if self.mainItem is None and not self.otherItems:
            return

        pass

    def autoAddPlusButtons(self, plusButtonFactory):
        """Dodaje plusy na wszystkich brzegach siatki."""
        pass