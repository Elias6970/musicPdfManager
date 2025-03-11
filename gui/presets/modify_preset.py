from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSlot, QEvent
from gui.status_console import StatusConsole
from gui.list_items.infinite_fields_item import InfiniteFieldsItem

# This class is a QWidget that contains a scroll area with a list of InfiniteFieldsItem
# The InfiniteFieldsItem is a QWidget that contains a copy number and a list of QLineEdit widgets
class ModifyPresetView(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.items:list[InfiniteFieldsItem] = []

        self.modify_scroll = StatusConsole()

        self.add_item()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.modify_scroll)

    #Add a new item to the scroll area. Only if the item_caller is the last item in the list
    #The function is called everytime that any lineedit get a change
    #   item_caller: The item that called this function
    def add_item(self,item_caller:InfiniteFieldsItem|None=None) -> None:
        if len(self.items) == 0 or item_caller == self.items[-1]:
            i = InfiniteFieldsItem(self.add_item,self)
            self.modify_scroll.add_item(i)
            self.items.append(i)
        self.resetTab()
    
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
        """Override the key press event to manage enter focus manually."""
        current_focus = self.focusWidget()

        if isinstance(current_focus, QLineEdit):
            current_index = self.items.index(self.findQLineEdit(current_focus))

            # Handle "Enter" key (next QLineEdit)
            # Enter jump to the first qlineedit of the next item
            if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                next_index = (current_index + 1) % len(self.items)
                self.items[next_index].instruments[0].setFocus()

        super().keyPressEvent(event)  # Call the base class handler to keep default behavior 
