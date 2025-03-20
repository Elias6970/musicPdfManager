import os,shutil,datetime
from typing import List
from classes.error import PdfNotFoundException
from classes.files_manage import Dir
from classes.constants import DIR_SCORES
from classes.classifier.exportable_pdf import ExportablePdf

#Object that controlls the pdfs ONLY IN ONE PIECE DIR
#   actual_pdf_number: index of the pdf in the dir(dir/scores)
#   actual_pdf_page: page of the actual pdf in scores dir
#   pdfs: list of ExportablePdf objects that have the path of the pdfs, their new names and the path to the temp file
#   
#   THROWS PdfNotFoundException()
class PdfController():
    def __init__(self,dir:Dir,actual_pdf_number=0) -> None:
        self.dir_path = dir.path

        self.actual_pdf_number:int = actual_pdf_number

        pdfs_paths:List[str] = [os.path.join(dir.path,DIR_SCORES,i) for i in dir.get_scores()]
        
        if pdfs_paths == []:
            raise PdfNotFoundException()
        
        self.pdfs:List[ExportablePdf] = [ExportablePdf(i) for i in pdfs_paths if os.path.isfile(i)]
         

    #return the actual pdf
    def get_actual_pdf(self):
        return self.pdfs[self.actual_pdf_number]

    #Move the original to a new folder to have a backup 
    #Return the folder name
    def move_originals(self) -> str:
        if not os.path.exists(os.path.join(self.dir_path,"partituras_sin_clasificar")):
            os.mkdir(os.path.join(self.dir_path,"partituras_sin_clasificar"))
       
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not os.path.exists(os.path.join(self.dir_path,"partituras_sin_clasificar",date)):
            os.mkdir(os.path.join(self.dir_path,"partituras_sin_clasificar",date))
            
        for i in self.pdfs:
            shutil.move(i.path,os.path.join(self.dir_path,"partituras_sin_clasificar",date,os.path.basename(i.path)))

        return date

    #Move from backup to scores and delete the original folder
    def move_from_backup_to_partituras(self,folder_name:str):
        backup_folder_path = os.path.join(self.dir_path,"partituras_sin_clasificar",folder_name)
        scores_folder_path = os.path.join(self.dir_path,DIR_SCORES)

        for i in os.listdir(backup_folder_path):
            if os.path.isfile(os.path.join(backup_folder_path,i)):
                shutil.move(os.path.join(backup_folder_path,i),scores_folder_path)

        shutil.rmtree(backup_folder_path)

    def export(self):
        backup_dir = self.move_originals()
        try:
            for i in self.pdfs:
                i.export()
        except Exception as e:
            print("Exception:", e," ",type(e))
            self.move_from_backup_to_partituras(backup_dir)
        