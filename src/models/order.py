"""Modelo de pedido."""
from datetime import datetime
from typing import Dict, Any, List, Optional

class Order:
    """Clase que representa un pedido."""

    def __init__(
        self,
        id: str,
        flores: List[Dict[str, Any]],
        cliente: Dict[str, Any],
        direccion: Dict[str, str],
        estado: str = "pendiente",
        fecha_creacion: Optional[datetime] = None
    ):
        self.id = id
        self.flores = flores
        self.cliente = cliente
        self.direccion = direccion
        self.estado = estado
        self.fecha_creacion = fecha_creacion or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el pedido a diccionario para MongoDB."""
        return {
            "id": self.id,
            "flores": self.flores,
            "cliente": self.cliente,
            "direccion": self.direccion,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        """Crea una instancia Order desde un diccionario de MongoDB."""
        return cls(
            id=data["id"],
            flores=data["flores"],
            cliente=data["cliente"],
            direccion=data["direccion"],
            estado=data["estado"],
            fecha_creacion=data.get("fecha_creacion")
        )