from PyQt6.QtCore import QRect, QSize, QRectF
from PyQt6.QtGui import QTransform
import fitz,tempfile,os,cv2
import numpy as np
from gui.interactive_previewer.movable_rectangle import MovableRectangle

# Class to save a crop to a rectangle
class CropRectangle:
    def __init__(self,rectangle:QRectF,rotation:float) -> None:
        self.rectangle = rectangle
        self.rotation = rotation
    
    
    def is_empty(self) -> bool:
        return self.rectangle.isEmpty()


    def get_rectangle_corners(self):
        local_corners = [
            self.rectangle.topLeft(),
            self.rectangle.topRight(),
            self.rectangle.bottomRight(),
            self.rectangle.bottomLeft(),
        ]
        rotated_corners = []
        
        center_x = (self.rectangle.topLeft().x() + self.rectangle.bottomRight().x()) / 2
        center_y = (self.rectangle.topLeft().y() + self.rectangle.bottomRight().y()) / 2
        rotation_rad = np.deg2rad(self.rotation)
        cos = np.cos(rotation_rad)
        sin = np.sin(rotation_rad)

        rotation_matrix = np.array([
            [cos,-sin],
            [sin,cos]
        ])
        for i in local_corners:
            translated = np.array([i.x()-center_x,i.y()-center_y])
            rotated = rotation_matrix @ translated
            rotated_corners.append([rotated[0]+center_x,rotated[1]+center_y])

        return np.array(rotated_corners)




    def extract_and_warp_rect(self,pixmap:fitz.Pixmap) -> fitz.Pixmap:
        """
        Extracts a rotated rectangle from a fitz.Pixmap and warps it to be upright.
        Can raise ValueError if the encoding is not good

        :param pixmap: fitz.Pixmap (input image)
        :param points: 4x2 NumPy array of the rectangle's corner points (clockwise or counter-clockwise)
        :return: Warped fitz.Pixmap
        """

        # Convert fitz.Pixmap to NumPy array (RGBA or grayscale)
        img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.h, pixmap.w, pixmap.n)

        # Ensure points are float32
        points = self.get_rectangle_corners()
        #print("NotRotated:",self.check_points())
        #print("Rotated:",list(points))
        #points = self.check_points()
        #points = np.array([[36,95],[518,35],[539,205],[57,265]])
        rect = np.array(points, dtype="float32")
        
        # Compute the new width and height of the upright rectangle
        width_a = np.linalg.norm(rect[0] - rect[1])
        width_b = np.linalg.norm(rect[2] - rect[3])
        max_width = int(max(width_a, width_b))

        height_a = np.linalg.norm(rect[0] - rect[3])
        height_b = np.linalg.norm(rect[1] - rect[2])
        max_height = int(max(height_a, height_b))

        # Define destination points for warping
        dst_rect = np.array([
            [0, 0], [max_width - 1, 0],
            [max_width - 1, max_height - 1], [0, max_height - 1]
        ], dtype="float32")

        # Compute perspective transformation matrix
        matrix = cv2.getPerspectiveTransform(rect, dst_rect)

        # Apply warp perspective transform
        warped_img = cv2.warpPerspective(img, matrix, (max_width, max_height))
        
        # Save or use the new pixmap
        #warped_pixmap.save("warped_output.png")
        rgb_image = cv2.cvtColor(warped_img, cv2.COLOR_BGR2RGB)
        #cv2.imwrite("output3332.png",rgb_image)
        #Encode the matlike img into png to be able to create the pixmap
        success, encoded_image = cv2.imencode('.png', rgb_image)
        if not success:
            raise ValueError("Image encoding failed.")

        # Create a Pixmap from the RGB image.
        pix = fitz.Pixmap(encoded_image.tobytes())

        return pix


    def crop(self,pdf_path:str) -> str:

        #print("Transpolated Rect:",self.get())
        #print("Points:",self.get_rectangle_corners())
        
        output_path = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        
        # A4 dimensions in points (1 point = 1/72 inch)
        a4_width, a4_height = 842, 595 # A4 size in points (portrait mode)

        file = fitz.open(pdf_path)
        original_pixmap = file[0].get_pixmap()
        file.close()
        
        warped_pixmap:fitz.Pixmap = self.extract_and_warp_rect(original_pixmap)
        #warped_pixmap.save("prueba.png")
        # Get original image size
        img_width = warped_pixmap.width
        img_height = warped_pixmap.height

        # Scale while maintaining aspect ratio
        scale_factor = min(a4_width / img_width, a4_height / img_height)
        new_width = (img_width * scale_factor) - 10
        new_height = (img_height * scale_factor) - 10

        # Centering image
        x_offset = (a4_width - new_width) / 2
        y_offset = (a4_height - new_height) / 2

        # Create a new PDF
        pdf = fitz.open()
        page = pdf.new_page(width=a4_width, height=a4_height)  # Create A4 page

        # Insert the Pixmap directly (no saving needed)
        page.insert_image(fitz.Rect(x_offset, y_offset, x_offset + new_width, y_offset + new_height),
                            pixmap=warped_pixmap)

        # Save PDF
        pdf.save(output_path)
        self.print_points(pdf_path)
        return output_path
    


    def print_points(self,pdf_path:str):
        corners = self.get_rectangle_corners()
        file = fitz.open(pdf_path)
        original_pixmap = file[0].get_pixmap()
        file.close()
        red=(255,0,0)
        for i in corners:
            for j in range(-1,2):
                for k in range(-1,2):
                    original_pixmap.set_pixel(int(i[0]+j),int(i[1]+k),red)
        
        #original_pixmap.set_pixel(30,30,(255,0,0))
        original_pixmap.save("salida.png")

        #raise Exception("Todo bien")
