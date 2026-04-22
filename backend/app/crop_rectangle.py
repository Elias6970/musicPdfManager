from PyQt6.QtCore import QRectF
import fitz,tempfile,os,cv2
import numpy as np

# Use a higher DPI than the preview so crops rely on the original PDF quality
RENDER_DPI = 300

# Class to save a crop to a rectangle
class CropRectangle:
    def __init__(self,rectangle:QRectF,rotation:float) -> None:
        self.rectangle = rectangle
        self.rotation = rotation
    
    
    def is_empty(self) -> bool:
        return self.rectangle.isEmpty()


    #Get the real 4 corners of the rectangle appliying the rotation
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




    def extract_and_warp_rect(self,pixmap:fitz.Pixmap, scale:float=1.0) -> tuple[bytes,int,int]:
        """
        Extracts a rotated rectangle from a fitz.Pixmap and warps it to be upright.
        Can raise ValueError if the encoding is not good

        :param pixmap: fitz.Pixmap (input image)
        :param scale: scale factor applied when rendering the pixmap (dpi/72)
        :return: Warped fitz.Pixmap
        """

        # Convert fitz.Pixmap to NumPy array (RGBA or grayscale)
        img = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.h, pixmap.w, pixmap.n)
        if pixmap.n == 4:
            # Convert RGBA to BGR
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            
        # Ensure points are float32
        points = self.get_rectangle_corners() * scale
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
        rgb_image = cv2.cvtColor(warped_img, cv2.COLOR_BGR2RGB)
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
        #Encode the matlike img into png to be able to create the pixmap
        success, encoded_image = cv2.imencode('.jpg', rgb_image,encode_params)
        if not success:
            raise ValueError("Image encoding failed.")

        # Create a Pixmap from the RGB image.
        #pix = fitz.Pixmap()

        return (encoded_image.tobytes(),max_width,max_height)

    #Crop a pdf with the selected rectangle and add it to a new a4 white pdf.
    #Your rectangle is scalled to fit the new pdf but keeping the aspect ratio.
    #Save the cropped pdf and return the path as a str
    #Can raise ValueError if appear errors in the pixmap of the pdf
    #   landscape: Create the final pdf landscape or portrait mode
    def crop(self,pdf_path:str,landscape:bool=True) -> str:
        output_path = os.path.join(tempfile.gettempdir(), os.urandom(24,).hex())
        
        # A4 dimensions in points (1 point = 1/72 inch)
        if landscape:
            a4_width, a4_height = 842, 595 # A4 size in points (landscape mode)
        else:
            a4_width, a4_height = 595, 842 # A4 size in points (portrait mode)
            
        # Render the page at higher DPI to avoid reusing the low‑res preview
        zoom = RENDER_DPI / 72  # PyMuPDF default is 72 dpi
        file = fitz.open(pdf_path)
        try:
            page = file[0]
            render_matrix = fitz.Matrix(zoom, zoom)
            original_pixmap = page.get_pixmap(matrix=render_matrix, alpha=False)
        finally:
            file.close()

        jpg_data, img_width, img_height = self.extract_and_warp_rect(original_pixmap, scale=zoom)
        #warped_pixmap.save("prueba.png")
        # Get original image size
        #img_width = warped_pixmap.width
        #img_height = warped_pixmap.height

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
                            stream=jpg_data)

        # Save PDF
        pdf.save(output_path)
        pdf.close()
        return output_path
    

    #Testing function to print the 4 corners of the selected rectangle
    def _print_points(self,pdf_path:str):
        corners = self.get_rectangle_corners()
        file = fitz.open(pdf_path)
        original_pixmap = file[0].get_pixmap()
        file.close()
        red=(255,0,0)
        for i in corners:
            for j in range(-1,2):
                for k in range(-1,2):
                    original_pixmap.set_pixel(int(i[0]+j),int(i[1]+k),red)
        
        original_pixmap.save("salida.png")
