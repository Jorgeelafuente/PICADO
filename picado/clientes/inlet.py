import re

from .. import ocr
from .base import ClienteBase


class Inlet(ClienteBase):
    nombre = "Inlet"
    palabras_clave = ["inletpack", "parc sagunt", "962 619 201", "albarán de salida"]

    def extraer(self, img, texto):
        return {
            "destinatario": self._destinatario(img),
            "pedido": self._pedido(texto),
            "palets": self.a_numero(self.buscar(r"Pall?ets?\s*[:;]\s*([\d.,]+)", texto)),
            "bultos": self.a_numero(self.buscar(r"Packages\s*[:;]\s*([\d.,]+)", texto)),
            "unidades": self.a_numero(self.buscar(r"quantity\s*[:;]\s*([\d.,]+)", texto)),
            "peso": self.a_numero(self.buscar(r"weight\s*[:;]\s*([\d.,]+)", texto)),
        }

    @staticmethod
    def _pedido(texto):
        m = re.search(r"SAL\s*([0-9OIl]{9})", texto)
        if not m:
            return ""
        digitos = m.group(1).replace("O", "0").replace("I", "1").replace("l", "1")
        return "SAL" + digitos

    @staticmethod
    def _destinatario(img):
        # Se lee solo el recuadro DESTINATARIO (arriba a la derecha) para no
        # mezclar el texto con el de la izquierda de la hoja.
        zona = ocr.recortar(img, 0.50, 0.06, 0.97, 0.20)
        lineas = [l.strip(" |_[]") for l in ocr.leer(zona).splitlines() if l.strip()]
        for i, linea in enumerate(lineas):
            if "destinatari" in linea.lower() and i + 1 < len(lineas):
                return lineas[i + 1]
        return ""
