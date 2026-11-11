import re
import unicodedata
from difflib import SequenceMatcher

CAMPOS = ["destinatario", "pedido", "palets", "bultos", "unidades", "peso"]


def _clave(texto):
    texto = unicodedata.normalize("NFD", texto or "")
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def _entero(valor):
    return int(round(valor))


def agrupar(hojas):
    """Une las hojas con el mismo cliente y destinatario en una sola fila."""
    grupos = []
    for h in hojas:
        clave = _clave(h.get("destinatario"))
        grupo = None
        if clave:
            for g in grupos:
                if g["cliente"] == h["cliente"] and g["clave"] and \
                        SequenceMatcher(None, g["clave"], clave).ratio() >= 0.85:
                    grupo = g
                    break
        if grupo is None:
            grupo = {
                "cliente": h["cliente"], "clave": clave,
                "destinatario": h.get("destinatario") or "",
                "pedidos": [], "palets": 0, "bultos": 0, "unidades": 0, "peso": 0.0,
                "paginas": [], "avisos": [],
            }
            grupos.append(grupo)

        pedido = h.get("pedido")
        if pedido and pedido not in grupo["pedidos"]:
            grupo["pedidos"].append(pedido)
        for campo in ("palets", "bultos", "unidades", "peso"):
            grupo[campo] += h.get(campo) or 0
        grupo["paginas"].append(h["pagina"])

        if h["cliente"] == "NO IDENTIFICADO":
            grupo["avisos"].append(f"hoja {h['pagina']}: cliente no identificado")
        else:
            for campo in CAMPOS:
                if h.get(campo) in (None, ""):
                    grupo["avisos"].append(f"hoja {h['pagina']}: falta {campo}")

    return [
        {
            "Cliente": g["cliente"],
            "Destinatario": g["destinatario"],
            "Pedidos": " / ".join(g["pedidos"]),
            "Palets": _entero(g["palets"]),
            "Bultos": _entero(g["bultos"]),
            "Unidades": _entero(g["unidades"]),
            "Peso": round(g["peso"], 2),
            "Hojas": ", ".join(str(p) for p in g["paginas"]),
            "Avisos": "; ".join(g["avisos"]),
        }
        for g in grupos
    ]
