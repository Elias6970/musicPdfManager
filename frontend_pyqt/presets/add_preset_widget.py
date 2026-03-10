from frontend_pyqt.pop_up_windows.yes_no_window import YesNoWindow
from frontend_pyqt.presets.abstract_modifying_preset_widget import AbstractModifyingPresetWidget


class AddPresetWidget(AbstractModifyingPresetWidget):
    """
    Widget to add a preset
        :param close_func: function called when you finish (added or cancelled) working with the preset.
    """
    
    def __init__(self, close_func, parent=None):
        super().__init__(close_func,parent)
        self.setWindowTitle(self.tr("Add new preset"))

        self.add_item() #Add first element


    def confirm(self):
        added_correctly = super().confirm()

        if added_correctly:
            self.reset()
            YesNoWindow(self.tr("Preset added correctly"),True,self)

        return added_correctly
    

    def reset(self):
        super().reset()

        self.add_item()
    

                
        
