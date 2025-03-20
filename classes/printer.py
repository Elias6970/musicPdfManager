import PyPDF2,os,tempfile
from reportlab.platypus import SimpleDocTemplate,Table
from reportlab.lib import pagesizes,colors
from reportlab.pdfgen import canvas
from classes.files_management.print_file import PrintFile
from classes.files_management.dir import Dir
from PyPDF2 import PdfWriter,PdfReader
from classes.validate import Validate
from classes.constants import DIR_SCORES,COVER_LIST_DOSSIER

#This class represents a printer saving a list of pdfs to print
class Printer:
    def __init__(self) -> None:
        self.actual_piece:Dir
        self.pdfs_added:list[PrintFile] = []
    
    def set_actual_piece(self,new_piece:Dir):
        self.actual_piece = new_piece

    def add_score(self,score_path:str,num_copies:int,pieces:list[str]) -> bool:
        #Stops the user if try to add a score no existing
        if Validate.validate_selection(self.actual_piece.name,pieces):

            self.pdfs_added.append(PrintFile(os.path.join(self.actual_piece.path,DIR_SCORES,score_path),num_copies))
            return True
        return False
    
    def create_pdf(self,path:str) -> None:
        merged_pdf = PyPDF2.PdfWriter()
        for i in self.pdfs_added:
            if os.path.exists(i.path):
                for j in range(i.copies): #Add the pdf the times that is selected in copies
                    merged_pdf.append(i.path)
        
        merged_pdf.write(path)
        merged_pdf.close()
    
    def delete_pdf(self,id:int) -> None:
        for i in self.pdfs_added:
            if i.id == id:
                self.pdfs_added.remove(i)
                break


#This class represents a dossier(list with information of the db)
class Dossier:
    #Export the pdf dossier with the list of scores to be printed
    @staticmethod
    def export_pdf_dossier_to_print(data:list,new_pdf_path:str,extra_cover_text:str):
        ENTRIES_PER_PAGE = 35
        CLOSING_EMPTY_ROWS = 120
        for _ in range(CLOSING_EMPTY_ROWS):
            data.append(("","","","",""))
        
        #Create a temp file because later we need to merge this pdf with the front page with the band logo
        temp_dossier = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())

        # Create a PDF document
        doc = SimpleDocTemplate(temp_dossier, pagesize=pagesizes.landscape(pagesizes.A4),topMargin=15,bottomMargin=20,leftMargin=5,rightMargin=5)
        

        # Customize table appearance
        cell_padding = 1.5
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), cell_padding),
            ('RIGHTPADDING', (0, 0), (-1, -1), cell_padding),
            ('TOPPADDING', (0, 0), (-1, -1), cell_padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), cell_padding),
        ]

        tables:list[Table] = []
        new_data = []
        counter = 0
        #Creates one table for each sheet
        for i,value in enumerate(data):
            new_data.append(value)

            counter += 1
            if counter >= ENTRIES_PER_PAGE or len(data) - 1 == i:
                new_data.insert(0,("Digitalizada","Cod","Nombre","Autor","tipo")) #traducir

                #Insert in the last page to don't have empty space
                if len(data)-1 == i:
                    for _ in range(ENTRIES_PER_PAGE - counter):
                        new_data.append(("","","","",""))
                
                #Create the table and add the columns
                aux_table = Table(new_data)
                #Set table
                aux_table._argW[0] = 60 #type:ignore
                aux_table._argW[1] = 30 #type:ignore
                aux_table._argW[2] = 295 #type:ignore
                aux_table._argW[3] = 200 #type:ignore
                aux_table._argW[4] = 200 #type:ignore
                aux_table.spaceAfter = 0
                aux_table.spaceBefore = 0
                aux_table.setStyle(style)

                tables.append(aux_table)

                counter = 0
                new_data = []


        #Modify the front page to put a string
        temp_overlay = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        canvas_overlay = canvas.Canvas(temp_overlay)
        canvas_overlay.setFont("Helvetica-Bold",30)
        canvas_overlay.drawString(453,70,extra_cover_text)
        canvas_overlay.save()
        

        #Merge in the same page the cover and the text
        cover_reader = PdfReader(COVER_LIST_DOSSIER())
        overlay_reader = PdfReader(temp_overlay)
        cover_reader.pages[0].merge_page(overlay_reader.pages[0])

        # Build the score list pdf
        doc.build(tables,onFirstPage=Dossier.footer,onLaterPages=Dossier.footer)

        
        #Merge the cover(portada) and the list of score names
        merged_pdf = PdfWriter()
        if os.path.exists(COVER_LIST_DOSSIER()) and os.path.exists(temp_dossier):
            merged_pdf.append(cover_reader)
            merged_pdf.append(temp_dossier)
        
        merged_pdf.write(new_pdf_path)
        merged_pdf.close()
        
        #Delete the temp file
        os.unlink(temp_dossier)


    #Put the number in the pages
    @staticmethod
    def footer(canvas:canvas.Canvas,doc:SimpleDocTemplate):
        canvas.saveState()
        pageNumber = canvas.getPageNumber()
        canvas.setFont("Helvetica", 10)
        canvas.drawString(pagesizes.landscape(pagesizes.A4)[0]/2 - 12, 13, str(pageNumber))
        canvas.restoreState()



