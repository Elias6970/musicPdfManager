from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import mm
import math,datetime


def crear_indice_pdf(
    lineas,
    title,
    subtitle=datetime.datetime.now().strftime("%d-%m-%Y"),
    archivo_salida="indice.pdf",
    max_columns=3,
    min_font_size=9,
    initial_font_size=12,
    font_name="Helvetica",
    title_font_name="Helvetica-Bold",
    subtitle_font_name="Helvetica-Oblique",
    left_margin= 20 * mm,
    bottom_margin= 5 * mm,
):
    title_space = 40 * mm  # Espacio para el título
    title_font_size = 40
    subtitle_font_size = 10

    # Configuración de página horizontal
    page_width, page_height = landscape(A4)

    # Crear canvas
    c = canvas.Canvas(archivo_salida, pagesize=(page_width, page_height))

    # Draw title
    c.setFont(title_font_name, title_font_size)
    title_width = stringWidth(title, font_name, title_font_size)
    title_x = (page_width - title_width) / 2
    title_y = page_height - (title_font_size * 1.2) - 5
    c.drawString(title_x, title_y, title)

    # Draw subtitle for the date
    c.setFont(subtitle_font_name, subtitle_font_size)
    subtitle_width = stringWidth(subtitle, subtitle_font_name, subtitle_font_size)
    subtitle_x = (page_width - subtitle_width) / 2
    subtitle_y = title_y - (subtitle_font_size * 1.5)
    c.drawString(subtitle_x, subtitle_y, subtitle)

    # Variables para cálculo
    usable_width = page_width - 2 * left_margin
    usable_height = page_height - 2 * bottom_margin - title_space

    # Intenta con distintos tamaños de fuente desde initial_font_size a min_font_size
    font_size = initial_font_size
    success = False

    while font_size >= min_font_size:
        # Calcular altura de línea
        line_height = font_size * 1.2

        # Probar con 1 hasta max_columns
        for num_columns in range(1, max_columns + 1):
            rows_per_column = int(usable_height // line_height)
            total_capacity = rows_per_column * num_columns

            if len(lineas) <= total_capacity:
                # Si caben, dibujar
                column_width = usable_width / num_columns
                c.setFont(font_name, font_size)

                for idx, texto in enumerate(lineas):
                    col = idx // rows_per_column
                    row = idx % rows_per_column
                    x = left_margin + col * column_width
                    y = page_height - bottom_margin - row * line_height - title_space
                    c.drawString(x, y, str(str(idx+1) + "- " + texto))

                c.save()
                print(f"Índice creado con tamaño de fuente: {font_size} y columnas: {num_columns}")
                success = True
                return

        # Reducir fuente
        font_size -= 1

    if not success:
        raise ValueError("Demasiados elementos para colocarlos en el índice dentro del espacio disponible.")


# Ejemplo de uso
if __name__ == "__main__":
    #lineas = [f"{i+1}- Report" for i in range(61)]  # Puedes probar con diferentes cantidades
    lineas = ['Zoraidamir', 'Solemnidad', 'Als Ligeros', 'Apostol Poeta', 'Abrahim Zulema', 'Aitana', 'Aquí, España', 'Bon Capitá', 'Capitania Cides 1986', 'Dos Parelles', 'Caballeria Ligera', 'El Tambor de Granaderos', 'Edward', 'Jesús Preso', 'Virgen del Castillo Viejo', 'Mater Mea', 'Mudejares', 'Petrer', 'Radetzky', 'Triunfal', 'Una Noche en Granada', 'Zulues de Petrer', 'Idella', 'Por los Jarales', 'Pas als Maseros', 'Abanderas', 'Guardia Jalifiana', 'Contrabandistas Valerosos', 'El Cristo del Perdón', 'Elda Musulmana', 'Misa Festera', 'Danzas Hugaras 5 y 6', 'Reina de Fiestas', 'Exodo Eslavo', 'Os Tres Galleguiños', 'Als Berebers', 'En Memoria De Mi Esposa', 'Pedro Díaz', 'Operador', 'Cristianos Monfortinos']
    crear_indice_pdf(
        lineas,
        title="Índice de Pasodobles",
        subtitle="Junio 2025",
        archivo_salida="indice_ejemplo.pdf",
        max_columns=2,
        min_font_size=9,
        initial_font_size=20
    )
