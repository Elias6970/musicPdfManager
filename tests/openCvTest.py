import cv2
import sys

img = cv2.imread(cv2.samples.findFile("gf.jpg"))

if img is None:
    sys.exit("Could not read the image.")
    
#cv2.rectangle(img,(1384,0),(2510,128),(100,230,50),-1)

cv2.imshow("Display window",img)

k = cv2.waitKey(0)

