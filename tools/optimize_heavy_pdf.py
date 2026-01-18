
import fitz, cv2, os
import numpy as np

def optimize_heavy_pdf(input_path: str, output_path: str):
    """
    Reads a PDF with heavy PNG images, converts them to Grayscale JPEGs,
    and saves a new lightweight PDF.
    """
    
    # 1. Open the heavy PDF
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    print(f"Processing: {input_path} ({len(doc)} pages)")

    for page_num, page in enumerate(doc):
        # 2. Find images on the current page
        image_list = page.get_images(full=True)
        
        # If the page has no images (or is just text), just copy it over as-is
        if not image_list:
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            continue

        # 3. Create a new page with the same dimensions
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)

        # We assume the main content is the first image (standard for scanned docs)
        # If you have multiple images per page, we could loop this, but usually scans have 1.
        xref = image_list[0][0]
        
        # 4. Get the location of the image on the page (so we don't lose your margins)
        # Note: get_image_bbox works on the image item from get_images
        img_rect = page.get_image_bbox(image_list[0])

        # 5. Extract the raw image data
        base_pix = fitz.Pixmap(doc, xref)
        
        # Convert to numpy array
        # fitz.Pixmap.samples gives raw bytes. We reshape based on height, width, channels (n)
        img_array = np.frombuffer(base_pix.samples, dtype=np.uint8).reshape(base_pix.h, base_pix.w, base_pix.n)

        # 6. OPTIMIZATION: Convert to Grayscale
        # If it has 3 channels (RGB), convert to Gray. If 4 (RGBA), convert too.
        if base_pix.n > 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

        # 7. OPTIMIZATION: Compress to JPEG
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
        success, jpeg_data = cv2.imencode('.jpg', img_array, encode_params)
        
        if not success:
            print(f"Warning: Failed to compress image on page {page_num}. Copying original.")
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            continue

        # 8. Insert the LIGHTWEIGHT JPEG into the new page
        new_page.insert_image(img_rect, stream=jpeg_data.tobytes())

    # 9. Save the result
    new_doc.save(output_path)
    new_doc.close()
    doc.close()
    
    # Calculate savings
    old_size = os.path.getsize(input_path)
    new_size = os.path.getsize(output_path)
    print(f"Done! Reduced {old_size/1024:.0f}KB -> {new_size/1024:.0f}KB")

for i in os.listdir("input"):
    if i.endswith(".pdf"):
        optimize_heavy_pdf(os.path.join("input", i), os.path.join("output", i))