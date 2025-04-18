from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout
from gui.status_console import StatusConsole
from gui.error_window import ShowError
from gui.list_items.infinite_comboboxes_item import InfiniteComboBoxesItem
from classes.presets.preset_manager import PresetManager
from classes.presets.preset import Preset
import re

# This class is a QWidget that contains a scroll area with a list of InfiniteFieldsItem
# The InfiniteComboBoxesItem is a QWidget that contains a copy number and a list of QComboboxes widgets
class AbstractModifyingPresetWidget(QWidget):
    """
    Abstract window to add/modify presets
        :param close_func: function called when you finish (added or cancelled) working with the preset.
    """
    def __init__(self, close_func, parent = None):
        super().__init__(parent)
        
        self.setMinimumSize(600,400)
        self.close_func = close_func

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
        

    
    #Add a new item to the scroll area if the item_caller is the last item in the list
    #The function is called everytime that any InfiniteComboBoxesItem's instrument atribute get a change
    #   item_caller: The item that called this function
    def add_item(self,item_caller:InfiniteComboBoxesItem|None=None) -> None:
        if len(self.items) == 0 or item_caller == self.items[-1]:
            i = InfiniteComboBoxesItem(self.add_item,parent=self)
            self.status_console.add_item(i)
            self.items.append(i)
        #self.resetTab()
    
    def force_add_empty_item(self) -> None:
        """Add an empty item without any check"""
        i = InfiniteComboBoxesItem(self.add_item,parent=self)
        self.status_console.add_item(i)
        self.items.append(i)


    def add_not_empty_item(self,copies:str|int,instruments_and_numbers:list[tuple[str,str]]) -> None:
        """Add an item with initial values"""
        item = InfiniteComboBoxesItem(self.add_item,0,self)
        item.num_copies.setCurrentText(copies)

        for i in instruments_and_numbers:
            item.add_instrument_combo(i[0],i[1])
        
        self.status_console.add_item(item)
        self.items.append(item)


    def parse_std_name(self,all:tuple[str,str]) -> str:
        """Return the instrument parsed name for a tuple of (istrument,number)"""
        if all[1].strip() == "":
            return all[0]
        return all[0] + "_" + all[1]


    def std_name_to_instrument_number(self,std_name:str) -> tuple[str,str]:
        """
        Extract instrument and number from the parsed name. 
        It returns (instrument,number). If it doesn't have number, it returns an emtpy str.
        """
        match = re.match(r"^(.*)_(\d+)$", std_name) #The first parenthesis captures the name, the second the number
        if match:
            return match.group(1), match.group(2)
        return std_name, ""
    

    def confirm(self) -> bool:
        """
        Save the new preset in the presets json file
        If everithing was fine return True, if not False
        """

        if self.preset_name.text().strip() == "":
            ShowError.show_tooltip_error(self.tr("You need to write the preset name"),5000,self.preset_name)
            return False
        elif self.preset_name.text() in self.preset_manager.get_names():
            ShowError.show_tooltip_error(self.tr("Already exist a preset with that name"),5000,self.preset_name)
            return False
        
        preset = Preset(self.preset_name.text())
        for i in self.items:
            if not i.is_empty():
                instrument = self.parse_std_name(i.instruments[0].get_instrument_and_number())

                if instrument.strip() == "":
                    ShowError.show_tooltip_error(self.tr("The main instrument can't be empty"),5000,i.instruments[0])
                    return False

                copies = i.num_copies.currentText()
                other_options:list[str] = []


                #Start in the second instrument because the fist one is the original
                for j in i.instruments[1:]:
                    if not j.is_empty():
                        parsed_name = self.parse_std_name(j.get_instrument_and_number())
                        other_options.append(parsed_name)
                
                preset.add_instrument(instrument,copies,other_options)

        self.preset_manager.add_preset(preset)
        self.preset_manager.dump()
        
        self.close()
        
        return True

    def close(self):
        self.close_func()



    def reset(self):
        """Reset the widget to the initial state."""
        self.preset_manager = PresetManager()
        self.preset_manager.load()
        self.items.clear()

        self.preset_name.clear()
        self.status_console.clear()



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