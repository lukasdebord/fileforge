"""
    prefix-fields.py -> contains widgets that support dragging and reordering
    filename prefix fields in the rename dialog.

    Last updated: 10/30/26
    Contributor: Copilot
"""

# imports
from PySide6.QtCore import (
    QByteArray,
    QMimeData,
    QPoint,
    Qt,
)
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QApplication, QLabel, QWidget


# ==================================================
# PREFIX FIELD DRAG AND DROP
# ==================================================

# MIME type used to identify a dragged prefix row.
_PREFIX_ROW_MIME_TYPE = "application/x-fileforge-prefix-row"


# --- DRAG HANDLE ---
class _PrefixDragHandle(QLabel):
    #Starts a drag from the row's handle after the pointer moves far enough.
    def __init__(self, row_widget):
        super().__init__("☰", row_widget)
        self.row_widget = row_widget
        self.drag_start_position = None
        self.setFixedWidth(20)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setToolTip("Drag to rearrange prefix fields")
        self.clear_drop_indicator = None

    # --- START DRAG ---
    def mousePressEvent(self, event):
        # Remember where the press began so a click does not trigger a drag.
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
            event.accept()
            return
        super().mousePressEvent(event)

    # --- UPDATE DRAG ---
    def mouseMoveEvent(self, event):
        # Start dragging only after Qt's standard movement threshold is crossed.
        if (
            self.drag_start_position is None
            or not event.buttons() & Qt.MouseButton.LeftButton
            or (event.position().toPoint() - self.drag_start_position).manhattanLength()
            < QApplication.startDragDistance()
        ):
            event.ignore()
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        # Carry the row identity because field text can change or be duplicated.
        mime_data.setData(
            _PREFIX_ROW_MIME_TYPE,
            QByteArray(str(id(self.row_widget)).encode()),
        )
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)
        if self.clear_drop_indicator is not None:
            self.clear_drop_indicator()
        self.drag_start_position = None

    # --- END DRAG ---
    def mouseReleaseEvent(self, event):
        self.drag_start_position = None
        super().mouseReleaseEvent(event)


# --- INDIVIDUAL ROW DROP TARGET ---
class _PrefixFieldRow(QWidget):
    # Accepts drops on a row and chooses before/after from the pointer position.
    def __init__(self, on_drop, on_drag_move):
        super().__init__()
        self.on_drop = on_drop
        self.on_drag_move = on_drag_move
        self.setAcceptDrops(True)

    # --- ACCEPT PREFIX ROW DRAG ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(_PREFIX_ROW_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    # --- UPDATE ROW DROP POSITION ---
    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat(_PREFIX_ROW_MIME_TYPE):
            event.ignore()
            return

        # The upper and lower halves of a row represent insertion before and after it.
        insertion_after = event.position().y() >= self.height() / 2
        self.on_drag_move(self, insertion_after)
        event.acceptProposedAction()

    # --- DROP ON ROW ---
    def dropEvent(self, event):
        if not event.mimeData().hasFormat(_PREFIX_ROW_MIME_TYPE):
            event.ignore()
            return

        # Pass the dragged row identity and selected insertion side to the dialog.
        source_row_id = int(bytes(event.mimeData().data(_PREFIX_ROW_MIME_TYPE)).decode())
        insertion_after = event.position().y() >= self.height() / 2
        self.on_drop(source_row_id, self, insertion_after)
        event.acceptProposedAction()


# --- PREFIX FIELDS DROP AREA ---
class _PrefixFieldsArea(QWidget):
    # Accepts drops over rows and gaps, and reports the matching insertion index.
    def __init__(self, get_rows, on_drop, on_drag_move, on_drag_leave):
        super().__init__()
        self.get_rows = get_rows
        self.on_drop = on_drop
        self.on_drag_move = on_drag_move
        self.on_drag_leave = on_drag_leave
        self.setAcceptDrops(True)

    # --- CALCULATE INSERTION INDEX ---
    def _insertion_index(self, y_position):
        # The first row midpoint below the pointer is where the dragged row belongs.
        for index, row in enumerate(self.get_rows()):
            row_top = row.mapTo(self, QPoint(0, 0)).y()
            if y_position < row_top + row.height() / 2:
                return index
        return len(self.get_rows())

    # --- ACCEPT PREFIX ROW DRAG ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(_PREFIX_ROW_MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    # --- UPDATE INSERTION INDICATOR ---
    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat(_PREFIX_ROW_MIME_TYPE):
            event.ignore()
            return

        # Recalculate the slot continuously so the indicator follows the pointer.
        self.on_drag_move(self._insertion_index(event.position().toPoint().y()))
        event.acceptProposedAction()

    # --- CLEAR INDICATOR WHEN DRAG LEAVES ---
    def dragLeaveEvent(self, event):
        self.on_drag_leave()
        super().dragLeaveEvent(event)

    # --- DROP IN FIELDS AREA ---
    def dropEvent(self, event):
        if not event.mimeData().hasFormat(_PREFIX_ROW_MIME_TYPE):
            event.ignore()
            return

        # Use the same slot calculation as the indicator to ensure the drop matches.
        source_row_id = int(bytes(event.mimeData().data(_PREFIX_ROW_MIME_TYPE)).decode())
        self.on_drop(source_row_id, self._insertion_index(event.position().toPoint().y()))
        event.acceptProposedAction()
