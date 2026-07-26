import re
from src.database.mongodb import get_database

db = get_database()
flowers_collection = db["flowers"]

def buscar_flores(nombre=None, color=None, precio_max=None):
    """Busca flores con filtros básicos"""
    query = {}
    
    if nombre:
        query["nombre"] = {"$regex": nombre, "$options": "i"}
    
    if color:
        query["color"] = {"$regex": color, "$options": "i"}
    
    if precio_max:
        query["precio"] = {"$lte": float(precio_max)}
    
    results = flowers_collection.find(query)
    return list(results)

def buscar_por_regex(patron, campo="nombre"):
    """Busca documentos usando una expresión regular personalizada"""
    try:
        regex = re.compile(patron, re.IGNORECASE)
        query = {campo: {"$regex": patron, "$options": "i"}}
        results = flowers_collection.find(query)
        return list(results)
    except re.error:
        return []

def obtener_todas_las_flores():
    """Obtiene todas las flores de la base de datos"""
    results = flowers_collection.find()
    return list(results)