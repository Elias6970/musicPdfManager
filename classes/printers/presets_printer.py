from concurrent.futures import ProcessPoolExecutor
from operator import index
from classes.utils.name_manager import NameManager
from classes.custom_order.instrument_sorter import InstrumentSorter
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
from reportlab.pdfbase.pdfmetrics import stringWidth
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
        self.add_index = False #If the exported pdfs should have an index page
        self.add_blank_page_after_index = False #If the exported pdfs should have a blank page after the index
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
    
    def set_add_index(self,t:bool) -> None:
        """Set if the exported pdfs should have an index page."""
        self.add_index = t

    def set_add_blank_page_after_index(self,t:bool) -> None:
        """Set if the exported pdfs should have a blank page after the index."""
        self.add_blank_page_after_index = t

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

    def create_export_folder(self,path:str) -> str:
        """Create the exporting folder in the given path and return its path"""
        exporting_folder = os.path.join(path,PresetsPrinter.EXPORTING_FOLDER_NAME)
        try:
            os.mkdir(exporting_folder)
        except FileExistsError:
            pass

        return exporting_folder

    
    def _process_piece_pdf(self,piece:str, instruments_order:list[str], exporting_folder:str) -> None:
        """
        Create a single PDF per piece by merging instrument PDFs in the given order.
        For each instrument in `instruments_order`, appends the resolved PDF for the
        specified `piece` as many times as its `copies` value indicates, skipping
        missing resolutions. The merged document is written to
        `exporting_folder/<piece>.pdf`.
        Args:
            piece (str): Name/identifier of the piece to export.
            instruments_order (list[str]): Ordered list of instrument names to merge.
            exporting_folder (str): Destination directory for the exported PDF.
        Returns:
            None
        """
        
        merge_pdf = pypdf.PdfWriter()

        for instrument in instruments_order:
            for _ in range(self._solution[instrument][piece].copies):
                pdf = self._solution[instrument][piece].resolution
                if pdf == None:
                    continue
                merge_pdf.append(pdf)
            
        merge_pdf.write(os.path.join(exporting_folder,piece)+".pdf")
        merge_pdf.close()          

    def export_by_pieces(self,path:str) -> None:
        """
        Generate all the pdf to print splitted by pieces
        """
        exporting_folder = self.create_export_folder(path)

        pieces = list(self._solution[list(self._solution.keys())[0]].keys())

        instruments_order = InstrumentSorter.sort_instruments(list(self._solution.keys()))

        tasks = []
        with ProcessPoolExecutor() as executor:
            for piece in pieces:
                future = executor.submit(self._process_piece_pdf,
                                         piece,
                                         instruments_order,
                                         exporting_folder)
                tasks.append(future)
            
            for task in tasks:
                try:
                    task.result()
                except Exception as e:
                    print(f"Error exporting instrument PDF: {e}")      
               
            

    def export_by_instruments(self,path:str) -> None:
        """
        Generate all the pdf to print splitted by instruments

        Args:
            path (str): The path where the pdfs will be exported
        """

        exporting_folder = self.create_export_folder(path)

        #Get the exporting order by the order added
        exporting_order:list[str] = [str(i.dir.name) for i in self.items]
        if self.sorted_export:
            exporting_order.sort(key=lambda x: NameManager.get_name(x))

        index = None
        if self.add_index:
            index = self._create_index([NameManager.get_name(m) for m in exporting_order], title="Índice de pasodobles")
        #Export the pieces in each pdf sorted by name
        tasks = []
        with ProcessPoolExecutor() as executor:
            for i in self._solution.keys():
                future = executor.submit(self._process_instrument_pdf,
                                            self.add_index,
                                            self.add_blank_page_after_index,
                                            self.add_cover_page,
                                            self.add_piece_number,
                                            index,
                                            exporting_order,
                                            self._solution,
                                            i,
                                            exporting_folder)
                tasks.append(future)

            for task in tasks:
                try:
                    task.result()
                except Exception as e:
                    print(f"Error exporting instrument PDF: {e}")
             
     

    def _process_instrument_pdf(self,
                                add_index:bool,
                                add_blank_page_after_index:bool,
                                add_cover_page:bool,
                                add_page_numbers:bool,
                                index_path:str,
                                exporting_order:list[str],
                                solution:dict[str,dict[str,ResolvedPresetInstrument]],
                                instrument:str,
                                exporting_folder:str) -> None:
            
            piece_num = 1 
            merge_pdf = pypdf.PdfWriter()

            if add_index:
                merge_pdf.append(index_path)
            
                if add_blank_page_after_index:
                    merge_pdf.add_blank_page(width=A4[1], height=A4[0]) #Landscape blank page

            for j in exporting_order:
                for _ in range(solution[instrument][j].copies):
                    pdf = solution[instrument][j].resolution
                    if pdf == None:
                        continue

                    if add_page_numbers:
                        pdf = self._add_page_number_to_pdf(pdf, piece_num)
                        piece_num += 1
                    merge_pdf.append(pdf)

            merge_pdf.write(os.path.join(exporting_folder,instrument)+".pdf")
            merge_pdf.close()   
            

    def _add_page_number_to_pdf(self, input_pdf:str, page_number:str|int) -> pypdf.PdfReader:
        """
        Add a page number to the first page of a PDF, respecting rotation and scaling to fit within a margin.
        The first page is rendered onto a new frame page that includes the page number,
        and the remaining pages are appended unchanged. The original rotation is flattened
        into the content so the resulting PDF has no `/Rotate` entry.
        Args:
            input_pdf (str): Path to the source PDF file.
            page_number (str | int): Page number text to place on the first page.
        Returns:
            pypdf.PdfReader: An in-memory PDF reader containing the modified document.
        """

        margin = 15  # Margin for the white frame

        reader = pypdf.PdfReader(input_pdf)
        writer = pypdf.PdfWriter()

        first_page = reader.pages[0]
        orig_width = first_page.mediabox.width
        orig_height = first_page.mediabox.height

        # Respect the rotation flag but flatten it into the content so the new PDF has no /Rotate entry.
        rotation = getattr(first_page, "rotation", 0) or first_page.get("/Rotate", 0) % 360
        angle = (-rotation) % 360  # Transformations rotate counterclockwise

        if angle in (90, 270):
            target_width, target_height = orig_height, orig_width
        else:
            target_width, target_height = orig_width, orig_height

        # Create the ReportLab frame page
        base_pdf = pypdf.PdfReader(self._create_white_background_page(target_width, target_height)).pages[0]

        scale_w = (target_width - margin) / target_width  # Scale factor to fit within the white frame
        scale_h = (target_height - margin) / target_height  # Scale factor to fit within the white frame
        scale_factor = min(scale_w, scale_h)
        #flattened_page.scale_by(scale_factor)

        # Center the scaled page within the frame
        final_scaled_height = target_height * scale_factor
        y_offset = base_pdf.mediabox.height - final_scaled_height



        transform = pypdf.Transformation().rotate(angle)
        if angle == 90:
            transform = transform.translate(orig_height, 0)
        elif angle == 180:
            transform = transform.translate(orig_width, orig_height)
        elif angle == 270:
            transform = transform.translate(0, orig_width)

        transform = transform.scale(scale_factor).translate(0, y_offset)

        # Merge shrunk content onto frame
        base_pdf.merge_transformed_page(first_page, transform)

        number_overlay = pypdf.PdfReader(self._create_number_overlay(target_width, target_height, str(page_number))).pages[0]
        base_pdf.merge_page(number_overlay)

        writer.add_page(base_pdf)
        writer.append(reader, pages=list(range(1, len(reader.pages))))

        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)
        return pypdf.PdfReader(buffer)


    def _create_white_background_page(self, width: float, height: float) -> io.BytesIO:
        """
        Create a ReportLab canvas with a white background.
        Args:
            width (float): Page width in points.
            height (float): Page height in points.

        Returns:
            io.BytesIO: Buffer containing the generated white background PDF.
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))

        # Draw white background (usually default is white anyway)
        c.setFillColorRGB(1, 1, 1) # White color
        c.rect(0, 0, width, height, fill=1, stroke=0)
        c.save()
        buffer.seek(0)
        return buffer


    def _create_number_overlay(self, width: float, height: float, number_text: str = "1") -> io.BytesIO:
        """
        Create a transparent PDF overlay with a page number at the bottom-right corner.
        Args:
            width (float): The width of the PDF page in points.
            height (float): The height of the PDF page in points.
            number_text (str, optional): The page number text to display. Defaults to "1".
        Returns:
            io.BytesIO: A buffer containing the generated PDF overlay.
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(width, height))
        
        # No background rect here, so it remains transparent!
        font_size = 25
        c.setFont("Helvetica-Bold", font_size)
        c.setFillColorRGB(0, 0, 0) # Black text

        if int(number_text) < 10:
            c.drawRightString(width - 11, 7, str(number_text))
        else:
            c.drawRightString(width - 7, 7, str(number_text))

        c.save()
        buffer.seek(0)
        return buffer
        
    def _fit_text_in_width(self, text:str, font_name:str, font_size:int, max_width:float) -> str:
        """Fit text within a specified width by truncating and adding ellipsis if necessary.
        Args:
            text (str): The text to fit.
            font_name (str): The font name to use.
            font_size (int): The font size to use.
            max_width (float): The maximum width in points.
        Returns:
            str: The fitted text, possibly truncated with ellipsis.
        """
        text_width = stringWidth(text, font_name, font_size)
        if text_width <= max_width:
            return text
        else:
            ellipsis_width = stringWidth("...", font_name, font_size)
            available_width = max_width - ellipsis_width
            fitted_text = ""
            for char in text:
                char_width = stringWidth(char, font_name, font_size)
                if stringWidth(fitted_text + char, font_name, font_size) <= available_width:
                    fitted_text += char
                else:
                    break
            return fitted_text + "..."
        
        
    def _create_index(self, 
                      elements:list[str], 
                      title:str = "Índice", 
                      subtitle=f"AM Virgen del Remedio {datetime.datetime.now().strftime("%d-%m-%Y")}",
                      output_path:str = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex()),
                      max_columns:int = 3,
                      min_font_size:int = 9,
                      initial_font_size:int = 18,
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
                        text = str(str(idx+1) + "- " + texto)
                        fitted_text = self._fit_text_in_width(text, font_name, font_size, column_width - 5) # 5 points padding
                        c.drawString(x, y, fitted_text)

                    c.save()
                    print(f"Índice creado con tamaño de fuente: {font_size} y columnas: {num_columns}")
                    success = True
                    return output_path

            # Reducir fuente
            font_size -= 1
        
    
        if not success:
            raise ValueError("Demasiados elementos para colocarlos en el índice dentro del espacio disponible.")

        return output_path
