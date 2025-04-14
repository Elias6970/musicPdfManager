from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QPushButton, QStackedWidget
from gui.status_console import StatusConsole
from gui.list_items.status_conosle_item_with_two_buttons import StatusConsleItemWithTwoButtons
from gui.presets.add_preset_widget import AddPresetWidget
from gui.presets.modify_preset_widget import ModifyPresetWidget
from classes.presets.preset_manager import PresetManager
from classes.config import PRESETS_PATH

class PresetsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset_manager = PresetManager()
        self.preset_manager.load(PRESETS_PATH)
        self.items:list[StatusConsleItemWithTwoButtons] = []

        self.setWindowTitle(self.tr("Presets"))

        self.stacked_widget = QStackedWidget()
        self.display_view = self.create_display_view()
        self.modify_view = self.create_modify_view()
        self.stacked_widget.addWidget(self.display_view)
        self.stacked_widget.addWidget(self.modify_view)
        
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.setMinimumSize(400,300)

        self.status_console.add_item(StatusConsleItemWithTwoButtons("Preset 1",3,2))


        # Relleno de presets
        for i in self.preset_manager.presets:
            self.add_preset_to_the_view(i.name)

        self.stacked_widget.setCurrentWidget(self.modify_view)

        self.exec()
        
        

    
    def create_display_view(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(30,30)
        self.add_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.modify_view))
        
       
        self.status_console = StatusConsole()
        self.status_console.setContentsMargins(10,0,10,5)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.status_console)

        widget.setLayout(layout)
        return widget


    def create_modify_view(self) -> QWidget:
        widget = AddPresetWidget(self)
        #widget = ModifyPresetWidget(self.preset_manager.get_preset("nuevo3"),self)
        return widget


    def add_preset_to_the_view(self,name:str):
        item = StatusConsleItemWithTwoButtons(name,self.modify_preset,self.remove_preset)
        self.status_console.add_item(item)
        self.items.append(item)

    def modify_preset(self,name:str):
        pass
    
    def remove_preset(self,name:str):
        self.preset_manager.remove_preset(name)
        for i in self.items:
            if i.name == name:
                self.status_console.remove_item(i)
                self.items.remove(i)
        
        print(self.preset_manager.presets)

    

    def closeEvent(self, a0):
        quit(0)



if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    win = PresetsWindow()
    app.exec()