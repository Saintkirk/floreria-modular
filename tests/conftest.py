"""
Configuración compartida para los tests.
Usa mongomock para simular MongoDB sin necesidad de un servidor real.
"""
import pytest
import mongomock
from pymongo.collection import Collection


@pytest.fixture
def mock_db():
    """Crea una base de datos mock de MongoDB."""
    client = mongomock.MongoClient()
    return client["floreria_db"]


@pytest.fixture
def mock_coleccion(mock_db):
    """Crea una colección mock de clientes."""
    return mock_db["clientes"]


@pytest.fixture
def cliente_ejemplo():
    """Documento de cliente de ejemplo para tests."""
    return {
        "nombre": "Juan Pérez",
        "rut": "12.345.678-5",
        "email": "juan@example.com",
        "telefono": "+56912345678",
        "direccion": {"calle": "Av. Siempre Viva", "numero": "123", "comuna": "Santiago"},
        "categoria_cliente": "Normal",
        "activo": True,
        "pedidos": [
            {
                "numero_pedido": "P001",
                "fecha_pedido": "2024-01-15",
                "ocasion": "Cumpleaños",
                "total": 25000,
                "estado": "Entregado",
                "productos": [
                    {"nombre": "Ramo de Rosas", "cantidad": 1, "precio": 25000}
                ]
            }
        ]
    }