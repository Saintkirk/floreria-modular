import uuid
from datetime import datetime
from src.models.order import Order
from src.database.mongodb import get_database

db = get_database()
orders_collection = db["orders"]

def crear_pedido(flores, cliente, direccion):
    """Crea un nuevo pedido en la base de datos"""
    order_id = str(uuid.uuid4())
    order = Order(
        id=order_id,
        flores=flores,
        cliente=cliente,
        direccion=direccion,
        estado="pendiente",
        fecha_creacion=datetime.now()
    )
    
    orders_collection.insert_one(order.to_dict())
    return order

def obtener_pedido(order_id):
    """Obtiene un pedido por su ID"""
    data = orders_collection.find_one({"id": order_id})
    if data:
        return Order.from_dict(data)
    return None

def actualizar_estado_pedido(order_id, nuevo_estado):
    """Actualiza el estado de un pedido existente"""
    result = orders_collection.update_one(
        {"id": order_id},
        {"$set": {"estado": nuevo_estado}}
    )
    return result.modified_count > 0

def agregar_pedido(order_data):
    """Método alternativo para agregar pedido (legacy)"""
    # Esta función puede ser removida si solo usas crear_pedido
    order_id = order_data.get('id', str(uuid.uuid4()))
    order = Order(
        id=order_id,
        flores=order_data.get('flores', []),
        cliente=order_data.get('cliente'),
        direccion=order_data.get('direccion'),
        estado=order_data.get('estado', 'pendiente'),
        fecha_creacion=datetime.now()
    )
    orders_collection.insert_one(order.to_dict())
    return order