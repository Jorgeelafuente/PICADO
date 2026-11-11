import re


class ClienteBase:
    nombre = "Base"
    palabras_clave = []  # textos que identifican a este cliente en sus albaranes

    def identifica(self, texto):
        """Cuántas palabras clave aparecen en la hoja (ignora espacios y mayúsculas)."""
        limpio = re.sub(r"\s+", "", texto.lower())
        return sum(
            1 for p in self.palabras_clave
            if re.sub(r"\s+", "", p.lower()) in limpio
        )

    def extraer(self, img, texto):
        """Devuelve un diccionario con destinatario, pedido, palets, bultos, unidades, peso."""
        raise NotImplementedError

    @staticmethod
    def buscar(patron, texto, flags=re.IGNORECASE):
        m = re.search(patron, texto, flags)
        return m.group(1).strip() if m else ""

    @staticmethod
    def a_numero(txt):
        """Convierte números en formato español: 6.480 -> 6480 ; 3.240,00 -> 3240.0"""
        if not txt:
            return None
        txt = re.sub(r"[^\d.,]", "", txt)
        if not txt:
            return None
        if "," in txt:
            txt = txt.replace(".", "").replace(",", ".")
        elif re.fullmatch(r"\d+\.\d{1,2}", txt):
            pass  # un punto con 1-2 decimales: es decimal
        else:
            txt = txt.replace(".", "")  # puntos de miles
        try:
            return float(txt)
        except ValueError:
            return None
