import PyPDF2,tempfile,shutil,cv2
import pandas as pd
import pytesseract
from matplotlib import pyplot as plt
from pdf2image import pdf2image
from thefuzz import fuzz

from backend.app.files_management.file import File
from backend.app.constants import OPTIONS_OF_INSTRUMENTS_ESP

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
        

        temp_pdf_rotated = tempfile.NamedTemporaryFile(delete=True)
        writer.write(temp_pdf_rotated.name)

        
        shutil.copy(temp_pdf_rotated.name,"tests/el_moro.pdf")
        #writer.write(open("tests/m.pdf",'wb'))
        #return temp_pdf_rotated
         

    #Transform pdf into jpg and get the pag selected
    def get_jpg(self,num_page):
        temp_jpg = tempfile.NamedTemporaryFile(suffix=".jpg",delete=True,)

        pdf = pdf2image.convert_from_path(self.path,200)
        for i, page in enumerate(pdf):
            if num_page == i:
                page.save(temp_jpg.name, 'JPEG')

        return temp_jpg

    #Detect the headers of the score(from the top to the first line of the first pentagram)
    def get_header(self,n_page):
        img_tmp = self.get_jpg(n_page)

        img = cv2.imread(img_tmp.name)
        
        lineLocations = self.findHorizontalLines(img_tmp.name)

        #Create a dataFrame(a table like sql) with two columns
        df_lineLocations = pd.DataFrame(lineLocations.sum(axis=1)).reset_index()
        df_lineLocations.columns = ['rowLoc', 'LineLength']
        
        #Create a df with the lines of df_lineLocation with Lenght > 0
        df_useful  = df_lineLocations[df_lineLocations['LineLength'] > 0]

        try:
            #Create a square from the top to the first line of the first pentagram)
            #I rest 10 to eliminate some notes over the pentagram
            cropped = img[0:int((df_useful.iloc[2])['rowLoc'])-10]
            
            #out_cropped = img[int((df_useful.iloc[0])['rowLoc'])-10:-1]
            #Save the header in a temporal file and return his object
            #tmp_header = tempfile.NamedTemporaryFile(suffix=".jpg",delete=True)
            #cv2.imwrite(tmp_header.name,cropped)
            

            #To print it
            
            """plt.figure(figsize=(8,8))
            plt.imshow(cropped)
            plt.waitforbuttonpress()"""

            return cropped
        
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




    def extract_header_text(self,num_page):
        tmp_img = self.get_header(num_page)
        img_rgb = cv2.cvtColor(tmp_img,cv2.COLOR_BGR2RGB) #type:ignore
       
        #print(pytesseract.get_languages())
        #print(pytesseract.image_to_string(img_rgb,lang='eng+cat+spa',config='--psm 12 -c preserve_interword_spaces=1'))
        av = pytesseract.image_to_data(img_rgb,lang='eng+cat+spa',config='--psm 12 -c preserve_interword_spaces=1',output_type="data.frame")
        
        posibilities = []
        for i in range(len(av)):
            a = self.check_instruments(str((av.iloc[i])['text']).upper())
            
            if a != None:
                #print(str((av.iloc[i])['text']),a)
                posibilities.append(a)

        posibilities = sorted(posibilities, key=lambda x:x[1],reverse=True)
       
        print(posibilities)
        #return posibilities


    def check_instruments(self,word):
        if(word != "NAN"):
            list = []
            for i in OPTIONS_OF_INSTRUMENTS_ESP:
                list.append((i,fuzz.token_sort_ratio(word,i)))
            
            return sorted(list, key=lambda x:x[1],reverse=True)[0]
        
        return None

