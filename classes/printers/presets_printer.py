from classes.printers.printer import Printer
from classes.printers.printeable_preset import PrinteablePreset
from classes.presets.preset import Preset
from classes.files_management.dir import Dir
from classes.presets.preset_resolver import PresetResolver, PresetResolverStates
from classes.presets.resolved_preset_instrument import ResolvedPresetInstrument
import pypdf,os

#This class represents a printer saving a list of pdfs to print
class PresetsPrinter(Printer):
    EXPORTING_FOLDER_NAME:str = "exported"

    def __init__(self) -> None:
        super().__init__()
        self.items:list[PrinteablePreset] = []
        self.sorted_export = False #Tell if the 
        self.ignore_preset_copies = False

        #
        self._solution:dict[str,dict[str,ResolvedPresetInstrument]] = {}

    def set_sorted_export(self,t:bool) -> None:
        self.sorted_export = t

    #Return the printeablePreset id to remove it from a list
    def add(self,copies:int,preset:Preset,dir:Dir) -> int:
        p = PrinteablePreset(copies)
        p.set_dir(dir)
        p.set_preset(preset)

        super().add(p)
        
        return p.id

    #Remove one element from the list
    def remove(self,id:int) -> bool:
        return super().remove(id)
        

    def export(self,path:str) -> None:
        #Resolve presets
        #Merge them
        pass


    def add_to_solution(self,resolved_preset_instrument:ResolvedPresetInstrument):
        """Add a resolved_preset_instrument to the solution"""

        if resolved_preset_instrument.instrument in self._solution:
            self._solution[resolved_preset_instrument.instrument][resolved_preset_instrument.piece] = resolved_preset_instrument
        else:
            self._solution[resolved_preset_instrument.instrument] = {resolved_preset_instrument.piece:resolved_preset_instrument}

    

    def preprocess_export(self) -> list[ResolvedPresetInstrument]:
        """
        Preprocess all the added pieces to check if exist score for all the preset's instruments
        It return a list of ResolvedPresetInstrument with all the presets instruments that don't have a score related
        """

        preset_resolver = PresetResolver()
        errors = []
        for i in self.items:
            resolution = preset_resolver.resolve(preset=i.preset, 
                                                 dir=i.dir,
                                                 ignore_copies=self.ignore_preset_copies)

            for j in resolution:
                if resolution != None and (j.state == PresetResolverStates.RESOLVED or
                                           j.state == PresetResolverStates.AUTO_RESOLVED):
                
                    self.add_to_solution(j)

                else:
                    errors.append(j)

        return errors


    def export_by_instruments(self,path:str):
        """Generate all the pdf to print splitted by instruments"""

        #Get the exporting order by the order added
        exporting_order:list = [i.dir.name for i in self.items]
        if self.sorted_export:
            exporting_order.sort()

        #Create folder in the path selected
        exporting_folder = os.path.join(path,PresetsPrinter.EXPORTING_FOLDER_NAME)
        try:
            os.mkdir(exporting_folder)
        except FileExistsError:
            pass

        #Export the pieces in each pdf sorted by name
        #for i in printeables.keys():
        for i in self._solution.keys():
            merge_pdf = pypdf.PdfWriter()

            for j in exporting_order:
                for _ in range(self._solution[i][j].copies):
                    merge_pdf.append(self._solution[i][j].resolution)

            merge_pdf.write(os.path.join(exporting_folder,i)+".pdf")
            merge_pdf.close()         

                

