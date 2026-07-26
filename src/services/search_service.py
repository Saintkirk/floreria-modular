from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo.collection import Collection
from bson.objectid import ObjectId

class SearchService:
    def __init__(self, db_collection: Collection):
        self.collection = db_collection

    def buscar_por_cliente(self, cliente_id: str) -> List[Dict]:
        """Busca pedidos por ID de cliente"""
        resultados = list(self.collection.find({"cliente_id": cliente_id}))
        for r in resultados:
            r["_id"] = str(r["_id"])
        return resultados

    def buscar_por_ocasion(self, ocasion: str) -> List[Dict]:
        """Busca pedidos por ocasión (case-insensitive)"""
        resultados = list(self.collection.find({"ocasion": {"$regex": ocasion, "$options": "i"}}))
        for r in resultados:
            r["_id"] = str(r["_id"])
        return resultados

    def buscar_por_estado(self, estado: str) -> List[Dict]:
        """Busca pedidos por estado"""
        resultados = list(self.collection.find({"estado": estado}))
        for r in resultados:
            r["_id"] = str(r["_id"])
        return resultados

    def buscar_por_fechas(self, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """Busca pedidos dentro de un rango de fechas (Compatible con mongomock)"""
        try:
            candidatos = list(self.collection.find())
            resultados = []
            start_str = fecha_inicio[:10] 
            end_str = fecha_fin[:10]

            for doc in candidatos:
                if "fecha_creacion" not in doc:
                    continue
                
                fecha_doc = doc["fecha_creacion"]
                if isinstance(fecha_doc, datetime):
                    fecha_str = fecha_doc.strftime("%Y-%m-%d")
                elif isinstance(fecha_doc, str):
                    fecha_str = fecha_doc[:10]
                else:
                    continue

                if start_str <= fecha_str <= end_str:
                    doc["_id"] = str(doc["_id"])
                    resultados.append(doc)
            
            return resultados
            
        except Exception as e:
            print(f"Error en búsqueda por fechas: {e}")
            return []

    def buscar_productos_en_pedidos(self, nombre_producto: str) -> List[Dict]:
        """Busca pedidos que contengan un producto específico"""
        query = {"productos.nombre": {"$regex": nombre_producto, "$options": "i"}}
        resultados = list(self.collection.find(query))
        for r in resultados:
            r["_id"] = str(r["_id"])
        return resultados

    # Función requerida explícitamente por los tests
    def buscar_por_regex(self, campo: str, valor: str) -> List[Dict]:
        """Búsqueda genérica por regex compatible con tests"""
        query = {campo: {"$regex": valor, "$options": "i"}}
        resultados = list(self.collection.find(query))
        for r in resultados:
            r["_id"] = str(r["_id"])
        return resultados