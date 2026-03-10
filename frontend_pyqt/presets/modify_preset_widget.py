from frontend_pyqt.pop_up_windows.yes_no_window import YesNoWindow
from frontend_pyqt.presets.abstract_modifying_preset_widget import AbstractModifyingPresetWidget
from backend.app.presets.preset import Preset
from backend.app.constants.constants import PRESETS_COPIES,PRESETS_OTHER_OPTIONS


class ModifyPresetWidget(AbstractModifyingPresetWidget):
    """
    Widget to modify an existing preset
        :param close_func: function called when you finish (added or cancelled) working with the preset.
    """

    def __init__(self, close_func, parent=None):
        super().__init__(close_func,parent)
        self.setWindowTitle(self.tr("Modify preset"))


    def fill(self,preset:Preset):
        """Fill the frontend_pyqt with the presest that is going to be modified"""
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
            self.reset()
            YesNoWindow(self.tr("Preset modified correctly"),True,self)
            
        return added_correctly
    

    def reset(self):
        super().reset()
    

    def load(self,preset:Preset):
        """Load a preset in the view"""
        self.fill(preset)
        #Remove the preset to add the new one. 
        #If the window is closed never happend because we are editing the obj not the presets.json 
        self.preset_manager.remove_preset(preset.name) 

