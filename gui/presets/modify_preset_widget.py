from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.presets.abstract_modifying_preset_widget import AbstractModifyingPresetWidget
from classes.presets.preset import Preset
from classes.constants.constants import PRESETS_COPIES,PRESETS_OTHER_OPTIONS


class ModifyPresetWidget(AbstractModifyingPresetWidget):
    """Widget to modify an existing preset"""

    def __init__(self, preset:Preset,parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Modify preset"))

        self.fill(preset)
        #Remove the preset to add the new one. 
        #If the window is closed never happend because we are editing the obj not the presets.json 
        self.preset_manager.remove_preset(preset.name) 


    def fill(self,preset:Preset):
        """Fill the gui with the presest that is going to be modified"""
        self.preset_name.setText(preset.name)

        for i in preset.instruments.keys():
            instrument,number = self.std_name_to_instrument_number(i)
            all_instruments_and_numbers:list[tuple[str,str]]= [(instrument,number)]
            copies = str(preset.instruments[i][PRESETS_COPIES])
            for j in preset.instruments[i][PRESETS_OTHER_OPTIONS]:
                all_instruments_and_numbers.append(self.std_name_to_instrument_number(j))
            
            self.add_not_empty_item(copies,all_instruments_and_numbers)
        
        self.force_add_empty_item()
        
    def confirm(self):
        added_correctly = super().confirm()

        if added_correctly:
            YesNoWindow(self.tr("Preset modified correctly"),True,self)
            self.hide()

        return added_correctly