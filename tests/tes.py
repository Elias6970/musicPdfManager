from matplotlib import pyplot as plt
import pandas as pd
import os,cv2
import fitz,tempfile,pytesseract

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

def a():
    path = get_image("tests\\gf.pdf")

    img = cv2.imread(path)
    lineLocations = findHorizontalLines(path)

    df_lineLocations = pd.DataFrame(lineLocations.sum(axis=1)).reset_index()
    
    df_lineLocations.columns = ['rowLoc', 'LineLength']
    
    
    a  = df_lineLocations[df_lineLocations['LineLength'] > 0]
    
    try:
        cropped = img[0:int((a.iloc[0])['rowLoc'])]
        print(pytesseract.image_to_string(cropped,"cat"))
        plt.figure(figsize=(8,8))
        plt.imsave("a.png",cropped)

    except Exception as e:
        print("fallo ", e)
    



if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    print(pytesseract.get_languages())
    a()