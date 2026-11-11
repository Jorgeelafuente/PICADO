from . import ocr
from .agrupar import agrupar
from .clientes import cargar_clientes


def procesar_pdf(contenido, avance=None):
    """Procesa un PDF. Devuelve (filas_resumen, detalle_por_hoja)."""
    clientes = cargar_clientes()
    hojas = []

    for numero, total, img in ocr.paginas(contenido):
        texto = ocr.leer(img)

        mejor, mejor_puntos = None, 0
        for cliente in clientes:
            puntos = cliente.identifica(texto)
            if puntos > mejor_puntos:
                mejor, mejor_puntos = cliente, puntos

        hoja = {"pagina": numero, "texto": texto}
        if mejor is None:
            hoja["cliente"] = "NO IDENTIFICADO"
        else:
            hoja["cliente"] = mejor.nombre
            hoja.update(mejor.extraer(img, texto))

        miniatura = img.copy()
        miniatura.thumbnail((900, 1300))
        hoja["miniatura"] = miniatura
        hojas.append(hoja)

        if avance:
            avance(numero, total)

    return agrupar(hojas), hojas
