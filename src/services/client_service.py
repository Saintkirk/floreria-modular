"""
Servicio de gestión de clientes (lógica de negocio).
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo.collection import Collection
from bson import ObjectId
from src.validators.chilean_validators import formatear_rut
from src.ui.colors import Colors
from src.ui.formatters import formatear_precio

def obtener_cliente_por_rut(coleccion: Collection, rut: str) -> Optional[Dict[str, Any]]:
    """Busca un cliente por su RUT formateado."""
    rut_formateado = formatear_rut(rut)
    return coleccion.find_one({"rut": rut_formateado})

def crear_cliente(coleccion: Collection, documento: Dict[str, Any]) -> Optional[ObjectId]:
    """
    Inserta un nuevo cliente en la base de datos.
    Args:
        coleccion: Colección de MongoDB.
        documento: Diccionario con todos los campos del cliente.
    Returns:
        ObjectId del documento insertado o None si falla.
    """
    try:
        resultado = coleccion.insert_one(documento)
        return resultado.inserted_id
    except Exception as e:
        print(f"{Colors.RED}✗ Error al crear cliente: {e}{Colors.END}")
        return None

def actualizar_campo(coleccion: Collection, cliente_id: ObjectId, campo: str, valor: Any) -> bool:
    """
    Actualiza un campo específico del documento raíz.
    Args:
        coleccion: Colección de MongoDB.
        cliente_id: ObjectId del cliente.
        campo: Ruta del campo a actualizar (ej: "nombre", "direccion.calle").
        valor: Nuevo valor del campo.
    Returns:
        True si la actualización fue exitosa.
    """
    try:
        coleccion.update_one({"_id": cliente_id}, {"$set": {campo: valor}})
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Error al actualizar: {e}{Colors.END}")
        return False

def eliminar_cliente(coleccion: Collection, cliente_id: ObjectId) -> bool:
    """Elimina un cliente por su ObjectId."""
    try:
        coleccion.delete_one({"_id": cliente_id})
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Error al eliminar: {e}{Colors.END}")
        return False

def mostrar_catalogo(db) -> list:
    """
    Muestra el catálogo de productos organizado por categoría.
    Args:
        db: Referencia a la base de datos.
    Returns:
        Lista de productos del catálogo.
    """
    catalogo = list(db["productos_catalogo"].find({}, {"_id": 0}))
    categorias: Dict[str, list] = {}
    for idx, prod in enumerate(catalogo, 1):
        cat = prod['categoria']
        categorias.setdefault(cat, []).append((idx, prod))
    num_global = 1
    for cat, prods in categorias.items():
        print(f"\n{Colors.BOLD}{cat}:{Colors.END}")
        for idx, prod in prods:
            print(f"    {Colors.CYAN}{num_global}.{Colors.END} {prod['nombre']} - {formatear_precio(prod['precio_base'])}")
            num_global += 1
    return catalogo