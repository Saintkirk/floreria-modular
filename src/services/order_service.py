"""
Servicio de gestión de pedidos (lógica de negocio).
"""
from datetime import datetime
from typing import Dict, Any, List
from pymongo.collection import Collection
from bson import ObjectId
from src.ui.colors import Colors
from src.ui.formatters import formatear_precio
from src.services.search_service import generar_numero_pedido


def agregar_pedido(coleccion: Collection, cliente_id: ObjectId, pedido: Dict[str, Any]) -> bool:
    """Agrega un nuevo pedido al array de pedidos del cliente."""
    try:
        coleccion.update_one({"_id": cliente_id}, {"$push": {"pedidos": pedido}})
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Error al agregar pedido: {e}{Colors.END}")
        return False


def actualizar_estado_pedido(coleccion: Collection, cliente_id: ObjectId, num_pedido: str, nuevo_estado: str) -> bool:
    """Actualiza el estado de un pedido específico."""
    try:
        coleccion.update_one(
            {"_id": cliente_id, "pedidos.numero_pedido": num_pedido},
            {"$set": {"pedidos.$.estado": nuevo_estado}}
        )
        return True
    except Exception as e:
        print(f"{Colors.RED} Error al actualizar estado: {e}{Colors.END}")
        return False


def agregar_producto_a_pedido(coleccion: Collection, cliente_id: ObjectId, num_pedido: str, producto: Dict[str, Any], nuevo_total: float) -> bool:
    """Agrega un producto a un pedido existente y recalcula el total."""
    try:
        coleccion.update_one(
            {"_id": cliente_id, "pedidos.numero_pedido": num_pedido},
            {"$push": {"pedidos.$.productos": producto}}
        )
        coleccion.update_one(
            {"_id": cliente_id, "pedidos.numero_pedido": num_pedido},
            {"$set": {"pedidos.$.total": nuevo_total}}
        )
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Error al agregar producto: {e}{Colors.END}")
        return False


def eliminar_pedido(coleccion: Collection, cliente_id: ObjectId, num_pedido: str) -> bool:
    """Elimina un pedido del array usando $pull."""
    try:
        coleccion.update_one(
            {"_id": cliente_id},
            {"$pull": {"pedidos": {"numero_pedido": num_pedido}}}
        )
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Error al eliminar pedido: {e}{Colors.END}")
        return False