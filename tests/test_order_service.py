"""Tests para el servicio de pedidos."""
from src.services.client_service import crear_cliente
from src.services.order_service import (
    agregar_pedido,
    actualizar_estado_pedido,
    eliminar_pedido,
)


class TestAgregarPedido:
    def test_agregar_pedido(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        nuevo_pedido = {
            "numero_pedido": "P002",
            "fecha_pedido": "2024-02-01",
            "ocasion": "Aniversario",
            "total": 30000,
            "estado": "Pendiente",
            "productos": []
        }
        resultado = agregar_pedido(mock_coleccion, cliente_id, nuevo_pedido)
        assert resultado is True
        doc = mock_coleccion.find_one({"_id": cliente_id})
        assert len(doc["pedidos"]) == 2


class TestActualizarEstadoPedido:
    def test_actualizar_estado(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = actualizar_estado_pedido(mock_coleccion, cliente_id, "P001", "Cancelado")
        assert resultado is True
        doc = mock_coleccion.find_one({"_id": cliente_id})
        assert doc["pedidos"][0]["estado"] == "Cancelado"


class TestEliminarPedido:
    def test_eliminar_pedido(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = eliminar_pedido(mock_coleccion, cliente_id, "P001")
        assert resultado is True
        doc = mock_coleccion.find_one({"_id": cliente_id})
        assert len(doc["pedidos"]) == 0