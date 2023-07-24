import cv2,PyPDF2
from matplotlib import pyplot as plt
import numpy as np
from pdf2image import pdf2image

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



def rotate():
    with open("gf.pdf",'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        for i in range(len(reader.pages)):
            p = reader.pages[i]
            p.rotate(180)
            writer.add_page(p)

        with open("rotate.pdf",'wb') as of:
            writer.write(of)
    
    pages = pdf2image.convert_from_path('rotate.pdf',200)

    for count, page in enumerate(pages):
        page.save(f'rotate.jpg', 'JPEG')

rotate()
lineLocations = findHorizontalLines("rotate.jpg")
#np.set_printoptions(threshold=np.inf)


plt.figure(figsize=(6,6))
plt.imshow(lineLocations, cmap='Greys')
plt.waitforbuttonpress()
