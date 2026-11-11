import io

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def paginas(contenido_pdf, zoom=3):
    """Convierte cada hoja del PDF en imagen. Devuelve (numero, total, imagen)."""
    doc = fitz.open(stream=contenido_pdf, filetype="pdf")
    total = len(doc)
    for i, pagina in enumerate(doc, start=1):
        pix = pagina.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
        yield i, total, Image.open(io.BytesIO(pix.tobytes("png")))


def leer(img, psm=6):
    """Lee el texto de una imagen con Tesseract (español)."""
    return pytesseract.image_to_string(img, lang="spa", config=f"--psm {psm}")


def recortar(img, x0, y0, x1, y1):
    """Recorta una zona usando fracciones de la hoja (0 a 1)."""
    ancho, alto = img.size
    return img.crop((int(ancho * x0), int(alto * y0), int(ancho * x1), int(alto * y1)))
