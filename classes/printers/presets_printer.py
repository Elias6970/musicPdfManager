from classes.utils.name_manager import NameManager
from classes.printers.printer import Printer
from classes.printers.printeable_preset import PrinteablePreset
from classes.presets.preset import Preset
from classes.files_management.dir import Dir
from classes.presets.preset_resolver import PresetResolver, PresetResolverStates
from classes.presets.resolved_preset_instrument import ResolvedPresetInstrument
from classes.files_management.archive import Archive
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import mm

import pypdf,os,io, tempfile, math, datetime


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
        exporting_order:list[str] = [str(i.dir.name) for i in self.items]
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
            merge_pdf.append(self._create_index([NameManager.get_name(m) for m in exporting_order], title="Índice de pasodobles"))

            for j in exporting_order:
                for _ in range(self._solution[i][j].copies):
                    pdf = self._solution[i][j].resolution
                    if pdf == None:
                        continue

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

        output_pdf = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        #output_pdf = input_pdf.replace(".pdf", f"_modified.pdf")
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
    

    def _create_index(self, 
                      elements:list[str], 
                      title:str = "Índice", 
                      subtitle=datetime.datetime.now().strftime("%d-%m-%Y"),
                      output_path:str = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex()),
                      max_columns:int = 3,
                      min_font_size:int = 9,
                      initial_font_size:int = 20,
                      font_name:str = "Helvetica",
                      title_font_name:str = "Helvetica-Bold",
                      subtitle_font_name:str = "Helvetica-Oblique",
                      left_margin:float = 20 * mm,
                      bottom_margin:float = 5 * mm,
                      title_space:float = 40 * mm, # Espacio para el título
                      title_font_size:int = 40,
                      subtitle_font_size:int = 10) -> str:
        """
        Create an index page with the given string elements.
            :param elements: List of strings to be included in the index. They will be generated in the order they are given.
            :param title: Title of the index page.
            :param subtitle: Subtitle of the index page, default is the current date.

            :return: The path to the generated PDF index file.

            :raises ValueError: If there are too many elements to fit in the index page with the given parameters.
        """



        # Configuración de página horizontal
        page_width, page_height = landscape(A4)

        # Crear canvas
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))

        # Draw title
        c.setFont(title_font_name, title_font_size)
        title_width = stringWidth(title, font_name, title_font_size)
        title_x = (page_width - title_width) / 2
        title_y = page_height - (title_font_size * 1.2) - 5
        c.drawString(title_x, title_y, title)

        # Draw subtitle for the date
        c.setFont(subtitle_font_name, subtitle_font_size)
        subtitle_width = stringWidth(subtitle, subtitle_font_name, subtitle_font_size)
        subtitle_x = (page_width - subtitle_width) / 2
        subtitle_y = title_y - (subtitle_font_size * 1.5) - 5
        c.drawString(subtitle_x, subtitle_y, subtitle)

        # Variables para cálculo
        usable_width = page_width - 2 * left_margin
        usable_height = page_height - 2 * bottom_margin - title_space

        # Intenta con distintos tamaños de fuente desde initial_font_size a min_font_size
        font_size = initial_font_size
        success = False

        while font_size >= min_font_size:
            # Calcular altura de línea
            line_height = font_size * 1.2

            # Probar con 1 hasta max_columns
            for num_columns in range(1, max_columns + 1):
                rows_per_column = int(usable_height // line_height)
                total_capacity = rows_per_column * num_columns

                if len(elements) <= total_capacity:
                    # Si caben, dibujar
                    column_width = usable_width / num_columns
                    c.setFont(font_name, font_size)

                    for idx, texto in enumerate(elements):
                        col = idx // rows_per_column
                        row = idx % rows_per_column
                        x = left_margin + col * column_width
                        y = page_height - bottom_margin - row * line_height - title_space
                        c.drawString(x, y, str(str(idx+1) + "- " + texto))

                    c.save()
                    print(f"Índice creado con tamaño de fuente: {font_size} y columnas: {num_columns}")
                    success = True
                    return output_path

            # Reducir fuente
            font_size -= 1
        
    
        if not success:
            raise ValueError("Demasiados elementos para colocarlos en el índice dentro del espacio disponible.")

        return output_path
