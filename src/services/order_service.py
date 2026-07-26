import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo.collection import Collection
from bson.objectid import ObjectId

# Alias para compatibilidad con tests antiguos
agregar_pedido = None 

class OrderService:
    def __init__(self, db_collection: Collection):
        self.collection = db_collection

    def crear_pedido(self, cliente_id: str, productos: List[Dict], ocasion: str, estado: str = "pendiente") -> Dict:
        """Crea un nuevo pedido"""
        pedido = {
            "_id": ObjectId(),
            "cliente_id": cliente_id,
            "productos": productos,
            "ocasion": ocasion,
            "estado": estado,
            "fecha_creacion": datetime.now(),
            "total": sum(p.get('precio', 0) * p.get('cantidad', 1) for p in productos)
        }
        result = self.collection.insert_one(pedido)
        pedido["_id"] = str(result.inserted_id)
        return pedido

    # Función requerida por los tests (Alias o implementación directa)
    def agregar_pedido(self, cliente_id: str, productos: List[Dict], ocasion: str, estado: str = "pendiente") -> Dict:
        """Alias de crear_pedido para compatibilidad con tests"""
        return self.crear_pedido(cliente_id, productos, ocasion, estado)

    def obtener_pedido(self, pedido_id: str) -> Optional[Dict]:
        """Obtiene un pedido por su ID"""
        try:
            pedido = self.collection.find_one({"_id": ObjectId(pedido_id)})
            if pedido:
                pedido["_id"] = str(pedido["_id"])
            return pedido
        except Exception:
            return None

    def listar_pedidos(self, limite: int = 10) -> List[Dict]:
        """Lista los últimos pedidos"""
        pedidos = list(self.collection.find().limit(limite).sort("fecha_creacion", -1))
        for p in pedidos:
            p["_id"] = str(p["_id"])
        return pedidos

    def agregar_producto_a_pedido(self, pedido_id: str, producto: Dict) -> Optional[Dict]:
        """Agrega un producto a un pedido existente (Compatible con mongomock)"""
        try:
            pedido_obj = self.collection.find_one({"_id": ObjectId(pedido_id)})
            if not pedido_obj:
                return None

            if "productos" not in pedido_obj:
                pedido_obj["productos"] = []
            
            pedido_obj["productos"].append(producto)
            nuevo_total = sum(p.get('precio', 0) * p.get('cantidad', 1) for p in pedido_obj["productos"])
            
            # Actualización segura sin operadores posicionales ($)
            self.collection.update_one(
                {"_id": ObjectId(pedido_id)},
                {"$set": {"productos": pedido_obj["productos"], "total": nuevo_total}}
            )
            
            pedido_obj["_id"] = str(pedido_obj["_id"])
            return pedido_obj
            
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            return None

    def actualizar_estado(self, pedido_id: str, nuevo_estado: str) -> bool:
        """Actualiza el estado de un pedido"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(pedido_id)},
                {"$set": {"estado": nuevo_estado}}
            )
            return result.modified_count > 0
        except Exception:
            return False

    def eliminar_pedido(self, pedido_id: str) -> bool:
        """Elimina un pedido"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(pedido_id)})
            return result.deleted_count > 0
        except Exception:
            return False

# Definir el alias global al final para asegurar que la clase esté definida
agregar_pedido = OrderService.agregar_pedido