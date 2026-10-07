from PyQt6 import QtCore, QtGui, QtWidgets
from collections.abc import Sequence
from typing import Protocol


class ScorePage(Protocol):
    @property
    def file_name(self) -> str: ...

    @property
    def page(self) -> int | None: ...

    @property
    def resolution(self) -> str | None: ...


class ScorePagesNavigator(QtWidgets.QWidget):
    page_selected = QtCore.pyqtSignal(int)
    CLASSIFIED_COLOR = QtGui.QColor("#16803c")
    CURRENT_PAGE_COLOR = QtGui.QColor("#fff2a8")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setUniformRowHeights(True)
        self.tree.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setStyleSheet(
            "QTreeWidget::item:selected {"
            "background-color: #fff2a8;"
            "color: #000000;"
            "}"
        )
        self.tree.itemClicked.connect(self._on_item_clicked)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self._score_items: dict[str, QtWidgets.QTreeWidgetItem] = {}
        self._page_items: dict[int, QtWidgets.QTreeWidgetItem] = {}

    def set_pages(self, pages: Sequence[ScorePage], current_index: int):
        if not self._page_items:
            self._build_tree(pages)

        classified_by_score: dict[str, int] = {}
        total_by_score: dict[str, int] = {}

        for page_index, page in enumerate(pages):
            score_name = page.file_name
            total_by_score[score_name] = total_by_score.get(score_name, 0) + 1
            if page.resolution is not None:
                classified_by_score[score_name] = classified_by_score.get(score_name, 0) + 1

            page_item = self._page_items.get(page_index)
            if page_item is not None:
                page_number = page.page + 1 if isinstance(page.page, int) else page_index + 1
                page_item.setText(0, page.resolution or self.tr("page %d") % page_number)
                page_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, page_index)
                page_item.setForeground(
                    0,
                    QtGui.QBrush(self.CLASSIFIED_COLOR) if page.resolution is not None else QtGui.QBrush(),
                )
                page_item.setBackground(0, QtGui.QBrush())
                if page_index == current_index:
                    page_item.setBackground(0, QtGui.QBrush(self.CURRENT_PAGE_COLOR))

        for score_name, score_item in self._score_items.items():
            classified_count = classified_by_score.get(score_name, 0)
            total_count = total_by_score.get(score_name, 0)
            score_item.setText(
                0,
                self.tr("%s (%d/%d)")
                % (score_name, classified_count, total_count),
            )
            score_item.setForeground(
                0,
                QtGui.QBrush(self.CLASSIFIED_COLOR)
                if total_count > 0 and classified_count == total_count
                else QtGui.QBrush(),
            )

        self._select_current_page(current_index)

    def _build_tree(self, pages: Sequence[ScorePage]):
        self.tree.clear()
        self._score_items.clear()
        self._page_items.clear()

        for page_index, page in enumerate(pages):
            score_item = self._score_items.get(page.file_name)
            if score_item is None:
                score_item = QtWidgets.QTreeWidgetItem([page.file_name])
                self.tree.addTopLevelItem(score_item)
                score_item.setExpanded(True)
                score_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, page_index)
                self._score_items[page.file_name] = score_item

            page_item = QtWidgets.QTreeWidgetItem([""])
            page_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, page_index)
            score_item.addChild(page_item)
            self._page_items[page_index] = page_item

    def _select_current_page(self, current_index: int):
        page_item = self._page_items.get(current_index)
        if page_item is None:
            self.tree.clearSelection()
            return

        self.tree.setCurrentItem(page_item)
        page_item.setSelected(True)
        parent = page_item.parent()
        if parent is not None:
            parent.setExpanded(True)

    def _on_item_clicked(self, item: QtWidgets.QTreeWidgetItem, column: int):
        page_index = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(page_index, int):
            self.page_selected.emit(page_index)