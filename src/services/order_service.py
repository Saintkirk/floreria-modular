"""
Servicio de gestión de pedidos (lógica de negocio).
"""
from datetime import datetime
from typing import Dict, Any, List
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from bson import ObjectId
from src.ui.colors import Colors
from src.ui.formatters import formatear_precio
from src.services.search_service import generar_numero_pedido

def agregar_pedido(coleccion: Collection, cliente_id: ObjectId, pedido: Dict[str, Any]) -> bool:
    """Agrega un nuevo pedido al array de pedidos del cliente."""
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id},
            {"$push": {"pedidos": pedido}}
        )
        return resultado.modified_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al agregar pedido: {e}{Colors.END}")
        return False

def actualizar_estado_pedido(coleccion: Collection, cliente_id: ObjectId, num_pedido: str, nuevo_estado: str) -> bool:
    """Actualiza el estado de un pedido específico."""
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id, "pedidos.numero_pedido": num_pedido},
            {"$set": {"pedidos.$.estado": nuevo_estado}}
        )
        return resultado.modified_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al actualizar estado: {e}{Colors.END}")
        return False

def agregar_producto_a_pedido(
    coleccion: Collection, 
    cliente_id: ObjectId, 
    num_pedido: str, 
    producto: Dict[str, Any], 
    nuevo_total: float
) -> bool:
    """
    Agrega un producto a un pedido existente y recalcula el total.
    Operación atómica para evitar inconsistencias.
    """
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id, "pedidos.numero_pedido": num_pedido},
            {
                "$push": {"pedidos.$.productos": producto},
                "$set": {"pedidos.$.total": nuevo_total}
            }
        )
        return resultado.modified_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al agregar producto: {e}{Colors.END}")
        return False

def actualizar_precio_producto(
    coleccion: Collection,
    cliente_id: ObjectId,
    num_pedido: str,
    indice_producto: int,
    nuevo_precio: float,
    nuevo_total: float
) -> bool:
    """Actualiza el precio de un producto específico en un pedido."""
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id, "pedidos.numero_pedido": num_pedido},
            {
                "$set": {
                    f"pedidos.$.productos.{indice_producto}.precio": nuevo_precio,
                    "pedidos.$.total": nuevo_total
                }
            }
        )
        return resultado.modified_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al actualizar precio: {e}{Colors.END}")
        return False

def eliminar_pedido(coleccion: Collection, cliente_id: ObjectId, num_pedido: str) -> bool:
    """Elimina un pedido del array usando $pull."""
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id},
            {"$pull": {"pedidos": {"numero_pedido": num_pedido}}}
        )
        return resultado.modified_count > 0
    except PyMongoError as e:
        print(f"{Colors.RED}✗ Error de MongoDB al eliminar pedido: {e}{Colors.END}")
        return False