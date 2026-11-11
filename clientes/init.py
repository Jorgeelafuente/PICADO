import importlib
import pkgutil

from .base import ClienteBase


def cargar_clientes():
    """Carga automáticamente todos los clientes de esta carpeta."""
    clientes = []
    for modulo_info in pkgutil.iter_modules(__path__):
        if modulo_info.name == "base" or modulo_info.name.startswith("_"):
            continue
        modulo = importlib.import_module(f"{__name__}.{modulo_info.name}")
        for obj in vars(modulo).values():
            if (
                isinstance(obj, type)
                and issubclass(obj, ClienteBase)
                and obj is not ClienteBase
                and obj.__module__ == modulo.__name__
            ):
                clientes.append(obj())
    return clientes
