"""
Servicio de gestión de pedidos (lógica de negocio).
"""
from typing import Optional, Dict, Any
from pymongo.collection import Collection
from bson import ObjectId


def agregar_pedido(coleccion: Collection, cliente_id: ObjectId, nuevo_pedido: Dict[str, Any]) -> bool:
    """
    Agrega un pedido a la lista de pedidos de un cliente.

    Args:
        coleccion: Colección de MongoDB.
        cliente_id: ObjectId del cliente.
        nuevo_pedido: Diccionario con los datos del pedido.

    Returns:
        True si el pedido fue agregado exitosamente.
    """
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id},
            {"$push": {"pedidos": nuevo_pedido}}
        )
        return resultado.modified_count > 0
    except Exception:
        return False


def actualizar_estado_pedido(coleccion: Collection, cliente_id: ObjectId, numero_pedido: str, nuevo_estado: str) -> bool:
    """
    Actualiza el estado de un pedido específico.

    Args:
        coleccion: Colección de MongoDB.
        cliente_id: ObjectId del cliente.
        numero_pedido: Número del pedido a actualizar.
        nuevo_estado: Nuevo estado del pedido.

    Returns:
        True si la actualización fue exitosa.
    """
    try:
        # Obtener el documento completo
        doc = coleccion.find_one({"_id": cliente_id})
        if not doc:
            return False

        # Buscar el pedido y actualizarlo
        pedidos = doc.get("pedidos", [])
        encontrado = False
        for pedido in pedidos:
            if pedido.get("numero_pedido") == numero_pedido:
                pedido["estado"] = nuevo_estado
                encontrado = True
                break

        if not encontrado:
            return False

        resultado = coleccion.update_one(
            {"_id": cliente_id},
            {"$set": {"pedidos": pedidos}}
        )
        return resultado.modified_count > 0
    except Exception:
        return False


def agregar_producto_a_pedido(
    coleccion: Collection,
    cliente_id: ObjectId,
    numero_pedido: str,
    producto: Dict[str, Any],
    nuevo_total: float
) -> bool:
    """
    Agrega un producto a un pedido existente y actualiza el total atómicamente.

    Args:
        coleccion: Colección de MongoDB.
        cliente_id: ObjectId del cliente.
        numero_pedido: Número del pedido.
        producto: Diccionario con los datos del producto.
        nuevo_total: Nuevo total del pedido.

    Returns:
        True si la operación fue exitosa.
    """
    try:
        # Obtener el documento completo
        doc = coleccion.find_one({"_id": cliente_id})
        if not doc:
            return False

        # Buscar el pedido y actualizarlo
        pedidos = doc.get("pedidos", [])
        encontrado = False
        for pedido in pedidos:
            if pedido.get("numero_pedido") == numero_pedido:
                pedido.setdefault("productos", []).append(producto)
                pedido["total"] = nuevo_total
                encontrado = True
                break

        if not encontrado:
            return False

        resultado = coleccion.update_one(
            {"_id": cliente_id},
            {"$set": {"pedidos": pedidos}}
        )
        return resultado.modified_count > 0
    except Exception:
        return False


def eliminar_pedido(coleccion: Collection, cliente_id: ObjectId, numero_pedido: str) -> bool:
    """
    Elimina un pedido de la lista de pedidos de un cliente.

    Args:
        coleccion: Colección de MongoDB.
        cliente_id: ObjectId del cliente.
        numero_pedido: Número del pedido a eliminar.

    Returns:
        True si el pedido fue eliminado exitosamente.
    """
    try:
        resultado = coleccion.update_one(
            {"_id": cliente_id},
            {"$pull": {"pedidos": {"numero_pedido": numero_pedido}}}
        )
        return resultado.modified_count > 0
    except Exception:
        return False