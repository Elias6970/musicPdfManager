import PyPDF2,tempfile,shutil,cv2
import pandas as pd
from matplotlib import pyplot as plt
from pdf2image import pdf2image

from classes.files_manage import File

class Pdf(File):
    def __init__(self, path):
        super(Pdf,self).__init__(path)

    #Rotate the pdf returning the object of the new pdf
    def rotate(self,degrees):

        reader = PyPDF2.PdfReader(self.path)
        writer = PyPDF2.PdfWriter()

        for i in range(len(reader.pages)):
            page = reader.pages[i]
            page.rotate(degrees)
            writer.add_page(page)
        

        temp_pdf_rotated = tempfile.NamedTemporaryFile(suffix=".pdf",delete=True)
        writer.write(temp_pdf_rotated)


        shutil.copy(temp_pdf_rotated.name,"a.pdf")

        return temp_pdf_rotated
         

    #Transform pdf into jpg and get the pag selected
    def get_jpg(self,num_page):
        temp_jpg = tempfile.NamedTemporaryFile(suffix=".jpg",delete=True,)

        pdf = pdf2image.convert_from_path(self.path,200)
        for i, page in enumerate(pdf):
            if num_page-1 == i:
                page.save(temp_jpg.name, 'JPEG')

        print(temp_jpg.name)

        return temp_jpg

    #Detect the headers of the score(from the top to the first line of the first pentagram)
    def get_header(self):
        img_tmp = self.get_jpg(1)

        img = cv2.imread(img_tmp.name)

        lineLocations = self.findHorizontalLines(img_tmp.name)

        #Create a dataFrame(a table like sql) with two columns
        df_lineLocations = pd.DataFrame(lineLocations.sum(axis=1)).reset_index()
        df_lineLocations.columns = ['rowLoc', 'LineLength']
        
        #Create a df with the lines of df_lineLocation with Lenght > 0
        df_useful  = df_lineLocations[df_lineLocations['LineLength'] > 0]
        
        try:
            #Create a square from the top to the first line of the first pentagram)
            cropped = img[0:int((df_useful.iloc[0])['rowLoc'])]
            
            #Save the header in a temporal file and return his object
            tmp_header = tempfile.NamedTemporaryFile(suffix=".jpg",delete=True)
            cv2.imwrite(tmp_header.name,cropped)
            
            return tmp_header

            #To print it
            """plt.figure(figsize=(8,8))
            plt.imshow(cropped)
            plt.waitforbuttonpress()"""

        except Exception as e:
            print("fallo ", e)
        
        

    #Find the lines in the score, in this case the lines of the pentagram
    def findHorizontalLines(self,img):
        img = cv2.imread(img) 
        
        #convert image to greyscale
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        # set threshold to remove background noise
        thresh = cv2.threshold(gray,30, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        
        # define rectangle structure (line) to look for: width 100, hight 1. This is a 
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (200,1))
        
        # Find horizontal lines
        lineLocations = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

        return lineLocations

