from pdf2image.pdf2image import convert_from_path

pages = convert_from_path('gf.pdf',200)

for count, page in enumerate(pages):
    page.save(f'gf.jpg', 'JPEG')

