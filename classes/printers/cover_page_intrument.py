from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
import os,tempfile,io


class CoverPageInstrument:
    """
    A class that represents a cover page when you export in the multiple selector byinstrument.
    The cover page has a title, the name of the instrument and an optional text to add maybe the name of the owner.
    """

    def __init__(self, title: str, instrument: str, text: str = "") -> None:
        self.title = title
        self.instrument = instrument
        self.text = text

    def get_cover_page(self):
        width, height = landscape(A4) # A4 size in points (595x842)

        buffer = io.BytesIO()

        c = canvas.Canvas(buffer, pagesize=(width, height))  

        # Optional: draw white background (usually default is white anyway)
        c.setFillColorRGB(1, 1, 1) # White color
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Draw page number in bottom-right corner
        c.setFont("Helvetica-Bold", 13)
        c.setFillColorRGB(0, 0, 0)

        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 50, self.title)

        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2, height / 2, self.instrument)

        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2, 60, self.text)

        c.save()
        buffer.seek(0)
        return buffer




    def __str__(self) -> str:
        return f"CoverPageInstrument(title={self.title}, instrument={self.instrument}, text={self.text})"