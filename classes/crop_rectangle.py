from PyQt6.QtCore import QRect, QSize, QRectF
from PyQt6.QtGui import QTransform
import fitz,tempfile,os,cv2
import numpy as np
from gui.interactive_previewer.movable_rectangle import MovableRectangle

# Class to save a crop to a rectangle
# Zoom is the relation between the original pixmap and the printed in the InteractivePreviewer
# Zoom = Original.width/Printed.width (we use width and not both because we are preserving the aspect ratio)
class CropRectangle:
    empty_rectangle = QRect(0,0,0,0)

    def __init__(self,movable_rect_item:MovableRectangle,zoom:float) -> None:
        self.zoom = zoom

        self.movable_rect_item = MovableRectangle()
        #self.movable_rect_item.setRect(movable_rect_item.rect())
        self.movable_rect_item.setPos(movable_rect_item.pos())
        self.movable_rect_item.setRotation(movable_rect_item.rotation())
        #self.movable_rect_item.setScale(self.zoom)
        
        topLeft = movable_rect_item.rect().topLeft() * zoom
        bottomRight = movable_rect_item.rect().bottomRight() * zoom

        rect = QRectF(topLeft,bottomRight)
        self.movable_rect_item.setRect(rect)


    #Get the rectangle to crop in the pdf
    #The rectangle is scaled to the pdf size
    def get(self) -> fitz.Rect:
        rect = self.movable_rect_item.get_rectangle().toRect()
        return rect
    
    
    def is_empty(self) -> bool:
        return self.movable_rect_item.get_rectangle().isEmpty()

    def get_rectangle_corners_2(self):
        rect = self.movable_rect_item.get_rectangle()
        
        local_corners = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomRight(),
            rect.bottomLeft(),
        ]
        rotated_corners = []
        
        center_x = (rect.topLeft().x() + rect.bottomRight().x()) / 2
        center_y = (rect.topLeft().y() + rect.bottomRight().y()) / 2
        rotation = np.deg2rad(self.movable_rect_item.rotation())
        cos = np.cos(rotation)
        sin = np.sin(rotation)

        for i in local_corners:
            x = center_x + cos * (i.x() - center_x) - sin * (i.y() - center_y)
            y = center_y + sin * (i.x() - center_x) - cos * (i.y() - center_y)
            #rotated.append([x,y])


        rotation_matrix = np.array([
            [cos,-sin],
            [sin,cos]
        ])
        for i in local_corners:
            translated = np.array([i.x()-center_x,i.y()-center_y])
            rotated = rotation_matrix @ translated
            rotated_corners.append([rotated[0]+center_x,rotated[1]+center_y])
            




        return np.array(rotated_corners)


    def get_rectangle_corners(self):
        """
        Extracts the four corner points of a rotated QGraphicsRectItem.

        :return: NumPy array of 4 corner points [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        """
        # Get the rectangle (x, y, width, height)
        rect = self.movable_rect_item.rect()

        # Define rectangle corner points in local coordinates
        local_corners = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomRight(),
            rect.bottomLeft(),
        ]

        # Get the transformation applied to the QGraphicsRectItem (rotation, scaling, etc.)
        transform = self.movable_rect_item.sceneTransform() if hasattr(self.movable_rect_item, 'sceneTransform') else QTransform()

        # Apply the transformation to each corner
        transformed_corners = [transform.map(point) for point in local_corners]

        # Convert to NumPy array
        points_array = np.array([[p.x(), p.y()] for p in transformed_corners], dtype=np.float32)

        return points_array

    def check_points(self):
        rect = self.movable_rect_item.get_rectangle()
        
        local_corners = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomRight(),
            rect.bottomLeft(),
        ]

        return local_corners

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
        points = self.get_rectangle_corners_2()
        print("NotRotated:",self.check_points())
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
        corners = self.get_rectangle_corners_2()
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
