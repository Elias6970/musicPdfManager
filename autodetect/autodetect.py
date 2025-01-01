import fitz,cv2,pytesseract
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

class CannotDetectOrientationException(Exception):
    pass


class Piece_to_classify:
    def __init__(self,name:str,instrument:str,num:int|str|None,orientation:int,pdf_pages:list[int]) -> None:
        self.name = name
        self.instrument = instrument
        self.num = num
        self.orientation = orientation
        self.pdf_pages = pdf_pages


class Detect:
    def __init__(self) -> None:
        self.pdf_path = ""
        self.piece_name = ""

    #Transform the pdf page into a gray scale array image
    def preprocess(self,page:fitz.Page):
        # Render page to a Pixmap
        pixmap = page.get_pixmap(dpi=200) #type:ignore

        # Convert Pixmap to NumPy array
        if pixmap.alpha:  # RGBA
            image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 4)
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)  # Convert to grayscale
        else:  # RGB
            image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 3)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Convert to grayscale
        
        return image
    
    #Detect if the image is horizontal or vertical (it doesn't detect if it is upside down)
    def is_horizontal(self,image):
        #binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)[1]
        binary = cv2.threshold(image,30, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Step 3: Detect edges
        edges = cv2.Canny(binary, 50, 150, apertureSize=3)
        
        # Step 4: Detect lines using Hough Transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            raise CannotDetectOrientationException
        
        # Step 5: Analyze line angles
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta)
            angles.append(angle)
        
        # Separate angles into horizontal and vertical groups
        vertical_lines = [angle for angle in angles if abs(angle - 90) > 45]
        horizontal_lines = [angle for angle in angles if abs(angle - 90) <= 45]

        # Step 6: Determine main orientation
        return len(horizontal_lines) > len(vertical_lines)
        

    def get_top_zone():


    def detect(self,piece_name:str,pdf_path:str):# -> Piece_to_classify:   
        for page in fitz.open(pdf_path):
            try:
                image = self.preprocess(page)
                
                #Rotate the image 90º clockwise
                if not self.is_horizontal(image):
                    image = cv2.transpose(image)
                    image = cv2.flip(image, 1)
                

                #Get top 


                cv2.imshow("h",image)
                cv2.waitKey(0)

            except CannotDetectOrientationException:
                pass



            