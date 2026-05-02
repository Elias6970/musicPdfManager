from PyQt6 import QtCore, QtWidgets


class MassiveImportResultWindow(QtWidgets.QDialog):
    def __init__(
        self,
        full_added_pieces: list[str] | None = None,
        pieces_without_files: list[str] | None = None,
        not_added_pieces: list[dict[str, str]] | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(self.tr("Massive Import Result"))
        self.setMinimumSize(720, 520)
        self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(12)

        intro_label = QtWidgets.QLabel(self.tr("Import completed. Review the results below."))
        intro_label.setWordWrap(True)
        main_layout.addWidget(intro_label)

        main_layout.addWidget(self._create_section(
            self.tr("Pieces fully added"),
            [self.tr("No pieces were fully added.")] if not full_added_pieces else full_added_pieces,
        ))
        main_layout.addWidget(self._create_section(
            self.tr("Pieces added without files"),
            [self.tr("No pieces were added without files.")] if not pieces_without_files else pieces_without_files,
        ))
        main_layout.addWidget(self._create_section(
            self.tr("Pieces not added due to errors"),
            [self.tr("No pieces failed during import.")] if not not_added_pieces else [f"{item['std_name']}: {item['error']}" for item in not_added_pieces],
        ))

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()

        self.ok_button = QtWidgets.QPushButton(self.tr("OK"))
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)

        main_layout.addLayout(buttons_layout)

    def _create_section(self, title: str, items: list[str]) -> QtWidgets.QWidget:
        section_widget = QtWidgets.QWidget()
        section_layout = QtWidgets.QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(6)

        title_label = QtWidgets.QLabel(title)
        title_font = title_label.font()
        title_font.setBold(True)
        title_label.setFont(title_font)
        section_layout.addWidget(title_label)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(120)

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(4)
        content_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        for item in items:
            item_label = QtWidgets.QLabel(item)
            item_label.setWordWrap(True)
            content_layout.addWidget(item_label)

        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        section_layout.addWidget(scroll_area)

        return section_widget