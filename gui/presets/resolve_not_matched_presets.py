from PyQt6 import QtWidgets,QtCore,QtGui
from gui.status_console import StatusConsole
from gui.list_items.status_console_item_with_two_texts_and_one_field import StatusConsoleItemWithTwoTextsAndOneField
from classes.presets.resolved_preset_instrument import ResolvedPresetInstrument
from classes.presets.preset_resolver_states import PresetResolverStates
from classes.files_management.dir import Dir
from classes.constants.constants import DIR_SCORES
import os

class ResolveNotMatchedPresets(QtWidgets.QDialog):
    def __init__(self,unresolved:list[ResolvedPresetInstrument],parent=None) -> None:
        super(ResolveNotMatchedPresets,self).__init__(parent)
        self.setWindowTitle(self.tr("Solve not autosolved scores"))
        self.status_console = StatusConsole()
        self.items:list[StatusConsoleItemWithTwoTextsAndOneField] = []
        self.unresolved = unresolved
        self.resolved:list[ResolvedPresetInstrument] = []

        self.btn_confirm = QtWidgets.QPushButton(self.tr("Confirm"))
        self.btn_confirm.clicked.connect(self.confirm)

        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(self.status_console)
        _layout.addWidget(self.btn_confirm)

        self.setLayout(_layout)

        #Genereate 
        for i in unresolved:
            if i.dir != None and i.state == PresetResolverStates.NOT_RESOLVED:
                item = StatusConsoleItemWithTwoTextsAndOneField(i.piece,
                                                               i.instrument,
                                                               i.dir.get_score_names_without_extension())
                self.status_console.add_item(item)
                self.items.append(item)
        


        self.exec()


    def confirm(self):
        for i in self.items:
            sol = i.get_selection()
            if sol == None: #Check if the score is unselected
                self.resolved.clear()
                return None
            piece,inst,score = sol

            for j in self.unresolved:
                if j.piece == piece and j.instrument == inst:
                    self.resolved.append(j)
                    self.resolved[-1].resolution = os.path.join(j.dir.path,DIR_SCORES,score) + ".pdf"
                    continue
                    
        self.hide()


            


