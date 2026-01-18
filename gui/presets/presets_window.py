from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QPushButton, QStackedWidget
from gui.elements.status_console import StatusConsole
from gui.elements.list_items.status_console_item_with_two_buttons import StatusConsoleItemWithTwoButtons
from gui.pop_up_windows.yes_no_window import YesNoWindow
from gui.presets.add_preset_widget import AddPresetWidget
from gui.presets.modify_preset_widget import ModifyPresetWidget
from classes.presets.preset_manager import PresetManager

class PresetsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset_manager = PresetManager()
        self.preset_manager.load()
        self.items:list[StatusConsoleItemWithTwoButtons] = []

        self.setWindowTitle(self.tr("Presets"))

        self.stacked_widget = QStackedWidget()
        self.display_view = self.create_display_view()
        self.add_preset_view = self.create_add_preset_view()
        self.modify_preset_view = self.create_modify_view()
        self.stacked_widget.addWidget(self.display_view)
        self.stacked_widget.addWidget(self.add_preset_view)
        self.stacked_widget.addWidget(self.modify_preset_view)
        
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.setMinimumSize(400,300)


        self.load_presets_in_the_console()

        self.stacked_widget.setCurrentWidget(self.display_view)

        self.exec()
        
        

    def create_display_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(30,30)
        self.add_btn.clicked.connect(lambda: self.show_add_preset_view())
        self.add_btn.setToolTip(self.tr("Add a new preset"))
        
       
        self.status_console = StatusConsole()
        self.status_console.setContentsMargins(10,0,10,5)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.status_console)

        widget.setLayout(layout)
        return widget


    def create_add_preset_view(self) -> AddPresetWidget:
        return AddPresetWidget(self.show_display_view,self)
    
    def create_modify_view(self) -> ModifyPresetWidget:
        return  ModifyPresetWidget(self.show_display_view,self)


    def load_presets_in_the_console(self):
        """Load all the presets in the preset_manager into the status_console"""
        # Relleno de presets
        for i in self.preset_manager.presets:
            self.add_preset_item_to_console(i.name,i.print())

    def add_preset_item_to_console(self,name:str,tool_tip:str):
        """Add a preset item to the list in the display view"""
        item = StatusConsoleItemWithTwoButtons(name,tool_tip,self.show_modify_preset_view,self.delete_preset)
        self.status_console.add_item(item)
        self.items.append(item)


    def show_add_preset_view(self):
        """Load the add preset view"""
        self.add_preset_view.reset()
        self.stacked_widget.setCurrentWidget(self.add_preset_view)


    def show_modify_preset_view(self,name:str):
        """Load the modifying preset view"""
        preset = self.preset_manager.get_preset(name)

        self.modify_preset_view.reset()
        self.modify_preset_view.load(preset)
        self.stacked_widget.setCurrentWidget(self.modify_preset_view)


    def show_display_view(self):
        """Load the display view"""
        #Reset the preset_manager and the list of presets
        self.preset_manager = PresetManager()
        self.preset_manager.load()
        self.items.clear()
        self.status_console.clear()
        self.load_presets_in_the_console()

        self.stacked_widget.setCurrentWidget(self.display_view)

    
    def delete_preset(self,name:str):
        """Delete a preset"""
        confirmation = YesNoWindow(self.tr("Are you sure that you want to delete preset ") + name, False, self)
        if confirmation.btn_confirm_pressed:
            self.preset_manager.remove_preset(name)
            self.preset_manager.dump()
            for i in self.items:
                if i.name == name:
                    self.status_console.remove_item(i)
                    self.items.remove(i)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    win = PresetsWindow()
    app.exec()