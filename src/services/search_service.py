"""
Servicio de búsquedas avanzadas en MongoDB.
"""
from datetime import datetime
from typing import List, Dict, Any
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from src.ui.colors import Colors
from src.ui.formatters import generar_regex_con_tildes

# Whitelist de operadores permitidos (Seguridad contra inyección)
OPERADORES_PERMITIDOS = {"$eq", "$gt", "$gte", "$lt", "$lte", "$ne", "$in", "$nin"}

def buscar_por_regex(coleccion: Collection, campo: str, patron: str) -> List[Dict[str, Any]]:
    """Busca documentos usando expresión regular con soporte de tildes y ñ."""
    try:
        regex_patron = generar_regex_con_tildes(patron)
        query = {campo: {"$regex": regex_patron, "$options": "i"}}
        return list(coleccion.find(query))
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB en búsqueda: {e}{Colors.END}")
        return []

def buscar_por_fechas(coleccion: Collection, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict[str, Any]]:
    """Busca pedidos dentro de un rango de fechas."""
    try:
        # Convertir fechas a formato string para compatibilidad con mongomock
        fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d")
        fecha_fin_dt = fecha_fin.replace(hour=23, minute=59, second=59)
        fecha_fin_str = fecha_fin_dt.strftime("%Y-%m-%d")
        
        # Buscar clientes que tengan al menos un pedido en el rango de fechas
        resultados = []
        for doc in coleccion.find():
            pedidos = doc.get("pedidos", [])
            for pedido in pedidos:
                fecha_pedido = pedido.get("fecha_pedido")
                if isinstance(fecha_pedido, str):
                    # Comparar strings directamente
                    if fecha_inicio_str <= fecha_pedido <= fecha_fin_str:
                        resultados.append(doc)
                        break
                elif isinstance(fecha_pedido, datetime):
                    # Comparar datetimes
                    if fecha_inicio <= fecha_pedido <= fecha_fin_dt:
                        resultados.append(doc)
                        break
        
        return resultados
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB en búsqueda: {e}{Colors.END}")
        return []

def buscar_por_comparacion(coleccion: Collection, ruta: str, operador: str, valor) -> List[Dict[str, Any]]:
    """Busca documentos usando operadores de comparación (con validación de seguridad)."""
    if operador not in OPERADORES_PERMITIDOS:
        print(f"{Colors.RED}✗ Error: Operador '{operador}' no permitido{Colors.END}")
        return []
    
    try:
        query = {ruta: {operador: valor}}
        return list(coleccion.find(query))
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB en búsqueda: {e}{Colors.END}")
        return []

def buscar_pedidos_por_rango_total(coleccion: Collection, pmin: float, pmax: float) -> List[Dict[str, Any]]:
    """Busca pedidos con total dentro de un rango usando $elemMatch."""
    try:
        query = {"pedidos": {"$elemMatch": {"total": {"$gte": pmin, "$lte": pmax}}}}
        return list(coleccion.find(query))
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB en búsqueda: {e}{Colors.END}")
        return []

def generar_numero_pedido(coleccion: Collection) -> str:
    """Genera el siguiente número de pedido secuencial (P001, P002, ...) de forma optimizada."""
    try:
        ultimo = coleccion.find_one(
            {"pedidos.numero_pedido": {"$regex": "^P\\d+$"}},
            {"pedidos": {"$elemMatch": {"numero_pedido": {"$regex": "^P\\d+$"}}}},
            sort=[("pedidos.numero_pedido", -1)]
        )
        
        max_num = 0
        if ultimo and "pedidos" in ultimo:
            for p in ultimo["pedidos"]:
                num = p.get("numero_pedido", "")
                if num.startswith("P") and num[1:].isdigit():
                    max_num = max(max_num, int(num[1:]))
        
        return f"P{max_num + 1:03d}"
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error al generar número de pedido: {e}{Colors.END}")
        return "P001"


def buscar_por_ocasion(coleccion: Collection, ocasion: str) -> List[Dict[str, Any]]:
    """Busca clientes que tengan pedidos con una ocasión específica usando $elemMatch."""
    try:
        query = {"pedidos": {"$elemMatch": {"ocasion": ocasion}}}
        return list(coleccion.find(query))
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB en búsqueda por ocasión: {e}{Colors.END}")
        return []


def buscar_por_estado(coleccion: Collection, estado: str) -> List[Dict[str, Any]]:
    """Busca clientes que tengan pedidos con un estado específico usando $elemMatch."""
    try:
        query = {"pedidos": {"$elemMatch": {"estado": estado}}}
        return list(coleccion.find(query))
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB en búsqueda por estado: {e}{Colors.END}")
        return []