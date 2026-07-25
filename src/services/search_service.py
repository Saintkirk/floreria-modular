"""
Servicio de búsquedas avanzadas en MongoDB.
Implementa búsquedas por regex, fechas, comparación y subdocumentos.
"""
from datetime import datetime
from typing import List, Dict, Any
from pymongo.collection import Collection
from src.ui.colors import Colors
from src.ui.formatters import formatear_precio, generar_regex_con_tildes
from src.config import CATEGORIAS, ESTADOS_PEDIDO, OCASIONES

def buscar_por_regex(coleccion: Collection, campo: str, patron: str) -> List[Dict[str, Any]]:
    """Busca documentos usando expresión regular con soporte de tildes y ñ."""
    regex_patron = generar_regex_con_tildes(patron)
    query = {campo: {"$regex": regex_patron, "$options": "i"}}
    return list(coleccion.find(query))

def buscar_por_fechas(coleccion: Collection, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict[str, Any]]:
    """Busca pedidos dentro de un rango de fechas (incluye el día final completo)."""
    fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
    query = {"pedidos.fecha_pedido": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    return list(coleccion.find(query))

def buscar_por_comparacion(coleccion: Collection, ruta: str, operador: str, valor) -> List[Dict[str, Any]]:
    """Busca documentos usando operadores de comparación de MongoDB."""
    query = {ruta: {operador: valor}}
    return list(coleccion.find(query))

def buscar_elemmatch(coleccion: Collection, pmin: float, pmax: float) -> List[Dict[str, Any]]:
    """Busca pedidos con total dentro de un rango usando $elemMatch."""
    query = {"pedidos": {"$elemMatch": {"total": {"$gte": pmin, "$lte": pmax}}}}
    return list(coleccion.find(query))

def generar_numero_pedido(coleccion: Collection) -> str:
    """Genera el siguiente número de pedido secuencial (P001, P002, ...)."""
    max_num = 0
    documentos = coleccion.find({}, {"pedidos.numero_pedido": 1})
    for doc in documentos:
        for p in doc.get("pedidos", []):
            num_str = p.get("numero_pedido", "")
            if num_str.startswith("P") and num_str[1:].isdigit():
                max_num = max(max_num, int(num_str[1:]))
    return f"P{max_num + 1:03d}"