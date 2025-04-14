from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.presets.abstract_modifying_preset_widget import AbstractModifyingPresetWidget


class AddPresetWidget(AbstractModifyingPresetWidget):
    """Widget to add a preset"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Add new preset"))

        self.add_item() #Add first element

    def confirm(self):
        added_correctly = super().confirm()

        if added_correctly:
            YesNoWindow(self.tr("Preset added correctly"),True,self)
            self.hide()

        return added_correctly
    

                
        
