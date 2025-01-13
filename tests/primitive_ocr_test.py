from matplotlib import pyplot as plt
import pandas as pd, numpy as np
import os,cv2
import fitz,tempfile,pytesseract

custom_config = r'--psm 11 --oem 3 --user-words instruments.txt -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"'

def findHorizontalLines(img):
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

#Returns a png path with the image
def get_image(pdf_path) -> str:  
    path =  os.path.join(tempfile.gettempdir(), os.urandom(24,).hex()+".png")
    file = fitz.open(pdf_path)
    page = file.load_page(0).get_pixmap(dpi=200) #type:ignore
    page.save(path)
    
    return path

#Paint in the image the lines founded
def paint_lines_found(img:cv2.typing.MatLike,lines:pd.DataFrame) -> cv2.typing.MatLike:
    copy_img = img.copy()
    for i,_ in enumerate(copy_img):
        if i in lines['rowLoc'].values:
            for j,_ in enumerate(img[i,:]):
                img[i,j] = [0,0,255]
    
    return copy_img

def a():
    path = get_image("tests\\gf.pdf")

    img = cv2.imread(path)
    #img = cv2.imread("tests\\hola.png")
    lineLocations = findHorizontalLines(path)

    df_lineLocations = pd.DataFrame(lineLocations.sum(axis=1)).reset_index()
    
    df_lineLocations.columns = ['rowLoc', 'LineLength']
    
    
    df_linesFound  = df_lineLocations[df_lineLocations['LineLength'] > 0]



    try:
        cropped = img[0:int((df_linesFound.iloc[0])['rowLoc'])]
        #map(lambda x: x if x in a['rowLoc'] else ,img)
        #re_cropped = cropped[:,0:int(cropped.shape[1]/3)]
        data = pytesseract.image_to_data(cropped,config=custom_config,output_type=pytesseract.Output.DATAFRAME)
        print(data[data['text'].notna()]["text"])

        #cv2.imwrite("hola.png",img)

    except Exception as e:
        print("fallo ", e)
    



if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    print(pytesseract.get_languages())
    a()