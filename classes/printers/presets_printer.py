from classes.printers.printer import Printer
from classes.printers.printeable_preset import PrinteablePreset
from classes.presets.preset import Preset
from classes.files_management.dir import Dir
from classes.presets.preset_resolver import PresetResolver, PresetResolverStates
from classes.presets.resolved_preset_instrument import ResolvedPresetInstrument
import pypdf,os,io,tempfile
from reportlab.pdfgen import canvas


#This class represents a printer saving a list of pdfs to print
class PresetsPrinter(Printer):
    EXPORTING_FOLDER_NAME:str = "exported"

    def __init__(self) -> None:
        super().__init__()
        self.items:list[PrinteablePreset] = []
        self.sorted_export = False #If the export should be sorted by name of the piece 
        self.ignore_preset_copies = False #If the export should ignore the copies of the presets
        self.add_piece_number = False #If the exported pdfs should have page numbers for each piece
        self.add_cover_page = False #If the exported pdfs should have a cover page
        #
        self._solution:dict[str,dict[str,ResolvedPresetInstrument]] = {}

    def set_sorted_export(self,t:bool) -> None:
        self.sorted_export = t

    def set_ignore_presets_copies(self,t:bool) -> None:
        self.ignore_preset_copies = t

    def set_add_piece_numbers(self,t:bool) -> None:
        """Set if the exported pdfs should have page numbers for each piece."""
        self.add_piece_number = t
    
    def set_add_cover_page(self,t:bool) -> None:
        """Set if the exported pdfs should have a cover page."""
        self.add_cover_page = t
        
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


    def export_by_instruments(self,path:str) -> None:
        """
        Generate all the pdf to print splitted by instruments

        Args:
            path (str): The path where the pdfs will be exported
        """

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

        piece_num = 1

        #Export the pieces in each pdf sorted by name
        for i in self._solution.keys():
            merge_pdf = pypdf.PdfWriter()

            for j in exporting_order:
                for _ in range(self._solution[i][j].copies):
                    pdf = self._solution[i][j].resolution
                    if self.add_piece_number:
                        pdf = self._add_page_number_to_pdf(pdf, piece_num)
                        piece_num += 1
                    merge_pdf.append(pdf)

            merge_pdf.write(os.path.join(exporting_folder,i)+".pdf")
            merge_pdf.close()         

    
    def _add_page_number_to_pdf(self, input_pdf:str, page_number:str|int) -> str:
        """
        Add a page number in the bottom-right to the first page of the pdf.

        returns the path to the new pdf with the page number added (temporally file).
        """
        margin = 15  # Margin for the white frame


        reader = pypdf.PdfReader(input_pdf)
        writer = pypdf.PdfWriter()

        first_page = reader.pages[0]
        orig_width = first_page.mediabox.width
        orig_height = first_page.mediabox.height

        # Create the ReportLab frame page
        frame_pdf = pypdf.PdfReader(self._create_frame_page(orig_width, orig_height, str(page_number))).pages[0]

        scale_w = (orig_width - margin) / orig_width  # Scale factor to fit within the white frame
        sacale_h = (orig_height - margin) / orig_height  # Scale factor to fit within the white frame
        first_page.scale_by(min(scale_w, sacale_h))  # Scale the first page content

        # Calculate offset to center within white frame
        y_offset = frame_pdf.mediabox.height - first_page.mediabox.height

        # Merge shrunk content onto frame
        frame_pdf.merge_translated_page(first_page, tx=0, ty=y_offset)

        writer.add_page(frame_pdf)

        # Add remaining pages unchanged
        for page in reader.pages[1:]:
            writer.add_page(page)

        #output_pdf = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        output_pdf = input_pdf.replace(".pdf", f"_modified.pdf")
        with open(output_pdf, "wb") as f:
            writer.write(f)
        
        return output_pdf

    def _create_frame_page(self, width, height, number_text="1"):
        """Create a ReportLab canvas with a white background and a page number in the bottom-right corner."""

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))

        # Optional: draw white background (usually default is white anyway)
        c.setFillColorRGB(1, 1, 1) # White color
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Draw page number in bottom-right corner
        c.setFont("Helvetica-Bold", 13)
        c.setFillColorRGB(0, 0, 0)

        # Adjust the position based on the number of digits
        if int(number_text) < 10:
            c.drawRightString(width - 11, 7, number_text)
        else:
            c.drawRightString(width - 7, 7, number_text)

        c.save()
        buffer.seek(0)
        return buffer