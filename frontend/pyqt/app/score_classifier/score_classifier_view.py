from PyQt6 import QtWidgets, QtCore, QtGui

from frontend.pyqt.app.config.constants import INSTRUCTIONS_SCORE_CLASSIFIER, ROTATE_L_IMG_PATH, ROTATE_R_IMG_PATH
from frontend.pyqt.app.score_classifier.interactive_previewer.interactive_previewer import InteractivePreviewer

class ScoreClassifierView(QtWidgets.QDialog):
    rotate_clockwise_signal = QtCore.pyqtSignal() 
    rotate_counterclockwise_signal = QtCore.pyqtSignal()
    previous_btn_signal = QtCore.pyqtSignal()
    continue_btn_signal = QtCore.pyqtSignal(str, bool, list) #str: name of the score, bool: if the rotation should be kept for the next page, list: corners of the selected area in the interactive previewer
    line_edit_text_changed_signal = QtCore.pyqtSignal(str) #str: text in the line edit, used to update the real time interpreted instrument label
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowTitle(self.tr("Score classifier")) #traducir 
        self.setMinimumSize(800, 630)
        self.init_ui()


    #Creates the user interface
    def init_ui(self):
        container_layout = QtWidgets.QVBoxLayout()
        rotate_btns_layout = QtWidgets.QVBoxLayout()
        btns_layout = QtWidgets.QHBoxLayout()
    
        #Menu bar
        help_opt = QtGui.QAction(self.tr("Help"),self) #traducir
        help_opt.triggered.connect(self.show_help)

        menu = QtWidgets.QMenuBar()
        menu.addAction(help_opt)


        #Pdf viewer
        self.interactive_previewer = InteractivePreviewer()
        self.interactive_previewer.setMinimumSize(600,400)

        #Rotate area
        btn_rotate_left = QtWidgets.QPushButton()
        btn_rotate_left.clicked.connect(self.rotate_counterclockwise_signal.emit)
        btn_rotate_left.setToolTip(self.tr("Rotate the pdf 90º to the left"))
        btn_rotate_left.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        btn_rotate_right = QtWidgets.QPushButton()
        btn_rotate_right.clicked.connect(self.rotate_clockwise_signal.emit)
        btn_rotate_right.setToolTip(self.tr("Rotate the pdf 90º to the right"))
        btn_rotate_right.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        
        try:
            btn_rotate_left.setIcon(QtGui.QIcon(ROTATE_L_IMG_PATH))
            btn_rotate_right.setIcon(QtGui.QIcon(ROTATE_R_IMG_PATH))
        except Exception:
            pass
        
        self.keep_rotation_cb = QtWidgets.QCheckBox(self.tr("Keep rotation to next scores"))
        self.keep_rotation_cb.setToolTip(self.tr("If this checkbox is checked the next pdf page is going to be rotated like the previous"))
        self.keep_rotation_cb.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        rotate_btns_horizontal_layout = QtWidgets.QHBoxLayout()
        rotate_btns_horizontal_layout.addWidget(btn_rotate_left)
        rotate_btns_horizontal_layout.addWidget(btn_rotate_right)

        rotate_btns_layout.addWidget(self.keep_rotation_cb)
        rotate_btns_layout.addLayout(rotate_btns_horizontal_layout)
        
        #buttons
        btn_prev = QtWidgets.QPushButton(self.tr("Previous"))
        btn_prev.clicked.connect(self.previous_btn_signal.emit)
        btn_prev.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.btn_next = QtWidgets.QPushButton("") # It is set in 
        self.change_to_continue_btn()
        self.btn_next.clicked.connect(lambda: self.continue_btn_signal.emit(self.line_edit.text(), 
                                                                       self.keep_rotation_cb.isChecked(),
                                                                       self.interactive_previewer.get_rectangle_corners()))
        self.btn_next.setAutoDefault(False)
        self.btn_next.setDefault(False)
        btn_close = QtWidgets.QPushButton(self.tr("Close"))
        btn_close.clicked.connect(self.hide)
        btn_close.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        btns_layout.addWidget(btn_prev)
        btns_layout.addWidget(self.btn_next)
        btns_layout.addWidget(btn_close)
        
        #Labels
        self.piece_name_lbl = QtWidgets.QLabel()
        self.piece_name_lbl
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.piece_name_lbl.setFont(font)

        #Last classified
        self.last_classfied_lbl = QtWidgets.QLabel()
        self.last_classfied_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.last_classfied_lbl.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        last_classfied_fixed_txt = QtWidgets.QLabel(self.tr("Last Name: ")) 
        last_classfied_fixed_txt.setFont(font)
        last_classfied_fixed_txt.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        last_classfied_fixed_txt.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)


        last_classfied_h_layout = QtWidgets.QHBoxLayout()
        last_classfied_h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        last_classfied_h_layout.addWidget(last_classfied_fixed_txt)
        last_classfied_h_layout.addWidget(self.last_classfied_lbl)


        #Writing line and instrument interpreter
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.returnPressed.connect(self.btn_next.click) #When you press enter pass to the next page
        self.line_edit.textChanged.connect(lambda text: self.line_edit_text_changed_signal.emit(text))

        self.interpreted_instrument_lbl = QtWidgets.QLabel()
        self.interpreted_instrument_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        writing_line_h_layout = QtWidgets.QHBoxLayout()
        writing_line_h_layout.addWidget(self.line_edit,3)
        writing_line_h_layout.addWidget(self.interpreted_instrument_lbl,1)

        #Add widgets
        container_layout.addWidget(self.piece_name_lbl)
        container_layout.addWidget(self.interactive_previewer)
        container_layout.addLayout(rotate_btns_layout)
        container_layout.addLayout(writing_line_h_layout)
        container_layout.addLayout(last_classfied_h_layout)

        container_layout.addLayout(btns_layout)
        

        # Shortcuts instructions
        self.instructions_lbl = QtWidgets.QLabel()
        self.instructions_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.shortcuts_scroll_area = QtWidgets.QScrollArea()
        self.shortcuts_scroll_area.setWidgetResizable(True)
        self.shortcuts_scroll_area.setWidget(self.instructions_lbl)
        self.shortcuts_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        shortcuts_lbl = QtWidgets.QLabel(self.tr("Shortcuts"))
        shortcuts_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        shortcuts_lbl.setContentsMargins(0, 0, 0, 2)

        shortcuts_layout = QtWidgets.QVBoxLayout()
        shortcuts_layout.addWidget(shortcuts_lbl)
        shortcuts_layout.addWidget(self.shortcuts_scroll_area)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setSpacing(5)
        main_layout.addLayout(shortcuts_layout)
        main_layout.addWidget(line)
        main_layout.addLayout(container_layout)
        main_layout.setMenuBar(menu)
        main_layout.setContentsMargins(10, 0, 10, 10)
        self.setLayout(main_layout)
    
    def change_to_finish_btn(self):
        """Set the button to finish and change its style to indicate the end of the classification process"""
        self.btn_next.setText(self.tr("Finish"))
        self.btn_next.setStyleSheet("background-color: green; color: white;")

    def change_to_continue_btn(self):
        """Set the button to continue and reset its style (in case it was changed to finish)"""
        self.btn_next.setText(self.tr("Continue"))
        self.btn_next.setStyleSheet("")

    def clear_line_edit(self):
        self.line_edit.clear()

    #Opens a pop up window with the instructions
    def show_help(self):
        QtWidgets.QMessageBox.information(self, self.tr("Help"), INSTRUCTIONS_SCORE_CLASSIFIER)

    def set_shortcuts(self, shortcuts: list[tuple[str, str]]):
        text = "\n".join([f"{name} -> {shortcut}" for name, shortcut in shortcuts])
        self.instructions_lbl.setText(text)
        
        font_metrics = QtGui.QFontMetrics(self.instructions_lbl.font())
        if not text:
            self.shortcuts_scroll_area.setFixedWidth(200)
            return
            
        instructions_lbl_width = max(font_metrics.horizontalAdvance(line) for line in text.split('\n'))
        instructions_lbl_width += 20 # Add some padding
        self.shortcuts_scroll_area.setFixedWidth(instructions_lbl_width)