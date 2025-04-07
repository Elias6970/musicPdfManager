from classes.printers.printer import Printer
from classes.printers.printeable_preset import PrinteablePreset
from classes.presets.preset import Preset
from classes.files_management.dir import Dir
from classes.presets.preset_resolver import PresetResolver, PresetResolverStates
from classes.presets.resolved_preset_instrument import ResolvedPresetInstrument
import pypdf,os,shutil
from collections import defaultdict

#This class represents a printer saving a list of pdfs to print
class PresetsPrinter(Printer):
    EXPORTING_FOLDER_NAME:str = "exported"

    def __init__(self) -> None:
        super().__init__()
        self.items:list[PrinteablePreset] = []
        #self.export_by_instruments = True #Default option
        self.export_sorted = False #Tell if the 
        self.ignore_preset_copies = False
    
    def set_export_sorted(self,t:bool) -> None:
        self.export_sorted = t

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
    
    
    #Preprocess to export the pdf
    #Return a tuple with:
    #   -dict of the valid solutions. Key=instrument string : value=dictionary with (key=piece_name string : value=ResolvedPresetInstrument)     
    #   -list of of ResolvedPresetInstrument that has been errors (not pdf founded for that instrument). 
    def preprocess_export(self) -> tuple[dict[str,dict[str,ResolvedPresetInstrument]],list]:
        preset_resolver = PresetResolver()
        #solution = defaultdict(dict)
        solution:dict = {}
        errors = []
        for i in self.items:
            resolution = preset_resolver.resolve(preset=i.preset, 
                                                 dir=i.dir,
                                                 ignore_copies=self.ignore_preset_copies)

            for j in resolution:
                if resolution != None and (j.state == PresetResolverStates.RESOLVED or
                                           j.state == PresetResolverStates.AUTO_RESOLVED):
                    
                    if j.instrument in solution:
                        solution[j.instrument][j.piece] = j 
                    else:
                        solution[j.instrument] = {j.piece:j}

                else:
                    errors.append(j)
        
        return (solution,errors)


    #Generate the pdfs to be printed
    def export_by_instruments(self,printeables:dict[str,dict[str,ResolvedPresetInstrument]],path:str):
        #Get the exporting order by the order added
        exporting_order:list = [i.dir.get_name_without_cod() for i in self.items]
        if self.export_sorted:
            exporting_order.sort()

        #Create folder in the path selected
        exporting_folder = os.path.join(path,PresetsPrinter.EXPORTING_FOLDER_NAME)
        try:
            os.mkdir(exporting_folder)
        except FileExistsError:
            pass

        #Export the pieces in each pdf sorted by name
        for i in printeables.keys():
            merge_pdf = pypdf.PdfWriter()

            for j in exporting_order:
                for _ in range(printeables[i][j].copies):
                    merge_pdf.append(printeables[i][j].resolution)

            merge_pdf.write(os.path.join(exporting_folder,i)+".pdf")
            merge_pdf.close()         

                

