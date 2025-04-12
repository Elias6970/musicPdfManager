from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSlot, QEvent
from gui.status_console import StatusConsole
from gui.list_items.infinite_comboboxes_item import InfiniteComboBoxesItem
from classes.presets.preset_manager import PresetManager

# This class is a QWidget that contains a scroll area with a list of InfiniteFieldsItem
# The InfiniteComboBoxesItem is a QWidget that contains a copy number and a list of QComboboxes widgets
class AbstractModifyingPresetWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.setMinimumSize(600,400)

        self.preset_manager = PresetManager()
        self.preset_manager.load()
        self.items:list[InfiniteComboBoxesItem] = []

        self.preset_name = QLineEdit()
        self.preset_name.setPlaceholderText(self.tr("New preset name"))

        self.status_console = StatusConsole()

        self.btn_confirm = QPushButton(self.tr("Confirm")) #traducir
        self.btn_cancel = QPushButton(self.tr("Cancel")) #traducir
        self.btn_confirm.clicked.connect(self.confirm)
        self.btn_cancel.clicked.connect(self.close)
        _btns_layout = QHBoxLayout()
        _btns_layout.addWidget(self.btn_confirm)
        _btns_layout.addWidget(self.btn_cancel)


        _layout = QVBoxLayout()
        _layout.addWidget(self.preset_name)
        _layout.addWidget(self.status_console)
        _layout.addLayout(_btns_layout)
        self.setLayout(_layout)
        
        
        self.add_item() #Add first element


    
    #Add a new item to the scroll area if the item_caller is the last item in the list
    #The function is called everytime that any InfiniteComboBoxesItem's instrument atribute get a change
    #   item_caller: The item that called this function
    def add_item(self,item_caller:InfiniteComboBoxesItem|None=None) -> None:
        if len(self.items) == 0 or item_caller == self.items[-1]:
            i = InfiniteComboBoxesItem(self.add_item,self)
            self.status_console.add_item(i)
            self.items.append(i)
        #self.resetTab()
    
    #It need to be implemented in the soon class
    def confirm(self):
        pass
    
    #It need to be implemented in the soon class
    def close(self):
        pass

    """
    #Reset the tab order to work with the dinamically added items
    def resetTab(self):
        print("Reset tab")
        previous_widget = None
        for item in self.items:  
            for line_edit in item.instruments:  # Loop through QLineEdit widgets inside each item
                if previous_widget:
                    self.setTabOrder(previous_widget, line_edit)    
                previous_widget = line_edit
            


    #Find the item that contains the QLineEdit widget
    def findQLineEdit(self,widget:QLineEdit):
        for item in self.items:
            for line_edit in item.instruments:
                if line_edit == widget:
                    return item
        return None
    

    def keyPressEvent(self, event: QEvent) -> None:
        current_focus = self.focusWidget()

        if isinstance(current_focus, QLineEdit):
            current_index = self.items.index(self.findQLineEdit(current_focus))

            # Handle "Enter" key (next QLineEdit)
            # Enter jump to the first qlineedit of the next item
            if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                next_index = (current_index + 1) % len(self.items)
                self.items[next_index].instruments[0].setFocus()

        super().keyPressEvent(event)  # Call the base class handler to keep default behavior 
    """