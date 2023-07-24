from matplotlib import pyplot as plt
import pandas as pd, numpy as np
import os,cv2
from pdf2image import pdf2image
import pandasql as ps

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



def a():
    #path = "../../score_examples/madera.jpg"
    path = "gf.jpg"
    #pages = pdf2image.convert_from_path('../../score_examples/madera.pdf',200)
    pages = pdf2image.convert_from_path('gf.pdf',200)
    for count, page in enumerate(pages):
        page.save(path, 'JPEG')

    img = cv2.imread(path)
    lineLocations = findHorizontalLines(path)

    df_lineLocations = pd.DataFrame(lineLocations.sum(axis=1)).reset_index()
    
    df_lineLocations.columns = ['rowLoc', 'LineLength']
    
    
    a  = df_lineLocations[df_lineLocations['LineLength'] > 0]
    
    try:
        cropped = img[0:int((a.iloc[0])['rowLoc'])]

        plt.figure(figsize=(8,8))
        plt.imshow(cropped)
        plt.waitforbuttonpress()
    except Exception as e:
        print("fallo ", e)

a()