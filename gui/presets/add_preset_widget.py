from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSlot, QEvent
from gui.status_console import StatusConsole
from gui.list_items.infinite_comboboxes_item import InfiniteComboBoxesItem
from gui.error_window import ShowError
from gui.presets.abstract_modifying_preset_widget import AbstractModifyingPresetWidget
from classes.presets.preset import Preset

class AddPresetWidget(AbstractModifyingPresetWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Add new preset"))


    def parse_std_name(self,all:tuple[str,str]) -> str:
        """Return the instrument parsed name for a tuple of (istrument,number)"""
        if all[1].strip() == "":
            return all[0]
        return all[0] + "_" + all[1]
    

    def confirm(self):
        """Save the new preset in the presets json file"""

        if self.preset_name.text().strip() == "":
            ShowError.show_tooltip_error(self.tr("You need to write the preset name"),5000,self.preset_name)
            return
        elif self.preset_name.text() in self.preset_manager.get_names():
            ShowError.show_tooltip_error(self.tr("Already exist a preset with that name"),5000,self.preset_name)
            return
        
        preset = Preset(self.preset_name.text())
        for i in self.items:
            if not i.is_empty():
                instrument = self.parse_std_name(i.instruments[0].get_instrument_and_number())
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
    

    def close(self):
        self.hide()
            
        
