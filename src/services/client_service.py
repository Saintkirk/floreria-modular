"""
Servicio de gestión de clientes (lógica de negocio).
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId
from src.validators.chilean_validators import formatear_rut
from src.ui.colors import Colors
from src.ui.formatters import formatear_precio

# Whitelist de campos actualizables
CAMPOS_ACTUALIZABLES = {
    "nombre", "email", "telefono", "categoria_cliente",
    "direccion.calle", "direccion.numero", "direccion.comuna",
    "activo", "notas"
}

def obtener_cliente_por_rut(coleccion: Collection, rut: str) -> Optional[Dict[str, Any]]:
    """Busca un cliente por su RUT formateado."""
    rut_formateado = formatear_rut(rut)
    return coleccion.find_one({"rut": rut_formateado})

def existe_rut(coleccion: Collection, rut: str) -> bool:
    """Verifica si un RUT ya está registrado."""
    rut_formateado = formatear_rut(rut)
    return coleccion.find_one({"rut": rut_formateado}) is not None

def existe_email(coleccion: Collection, email: str) -> bool:
    """Verifica si un email ya está registrado."""
    return coleccion.find_one({"email": email}) is not None

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
    except DuplicateKeyError:
        print(f"{Colors.RED}✗ Error: Documento duplicado (RUT o Email ya existe){Colors.END}")
        return None
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al crear cliente: {e}{Colors.END}")
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
        True si la actualización fue exitosa y modificó algo.
    """
    if campo not in CAMPOS_ACTUALIZABLES:
        print(f"{Colors.RED}✗ Error: Campo '{campo}' no es actualizable{Colors.END}")
        return False
    
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id},
            {"$set": {campo: valor}}
        )
        return resultado.modified_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al actualizar: {e}{Colors.END}")
        return False

def eliminar_cliente(coleccion: Collection, cliente_id: ObjectId) -> bool:
    """Elimina un cliente por su ObjectId."""
    try:
        resultado = coleccion.delete_one({"_id": cliente_id})
        return resultado.deleted_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al eliminar: {e}{Colors.END}")
        return False

def eliminar_cliente_por_rut(coleccion: Collection, rut: str) -> bool:
    """Elimina un cliente por su RUT."""
    rut_formateado = formatear_rut(rut)
    try:
        resultado = coleccion.delete_one({"rut": rut_formateado})
        return resultado.deleted_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al eliminar: {e}{Colors.END}")
        return False

def eliminar_clientes_por_filtro(coleccion: Collection, filtro: Dict[str, Any]) -> int:
    """Elimina múltiples clientes según un filtro."""
    try:
        resultado = coleccion.delete_many(filtro)
        return resultado.deleted_count
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al eliminar: {e}{Colors.END}")
        return 0

def obtener_catalogo(db: Database) -> list:
    """
    Obtiene el catálogo de productos de la base de datos.
    
    Args:
        db: Referencia a la base de datos.
    
    Returns:
        Lista de productos del catálogo.
    """
    return list(db["productos_catalogo"].find({}, {"_id": 0}))

def mostrar_catalogo(catalogo: list) -> None:
    """
    Muestra el catálogo de productos organizado por categoría.
    
    Args:
        catalogo: Lista de productos a mostrar.
    """
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