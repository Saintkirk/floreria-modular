"""Tests para el servicio de pedidos."""
import pytest
from src.services.client_service import crear_cliente
from src.services.order_service import (
    agregar_pedido,
    actualizar_estado_pedido,
    agregar_producto_a_pedido,
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


class TestAgregarProductoAPedido:
    def test_agregar_producto_atomico(self, mock_coleccion, cliente_ejemplo):
        """Test de operación atómica: producto y total se actualizan juntos."""
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        
        producto = {"nombre": "Girasoles", "cantidad": 2, "precio": 18000}
        nuevo_total = 25000 + (2 * 18000)  # Total original + nuevo producto
        
        resultado = agregar_producto_a_pedido(
            mock_coleccion, cliente_id, "P001", producto, nuevo_total
        )
        
        assert resultado is True
        doc = mock_coleccion.find_one({"_id": cliente_id})
        pedido = doc["pedidos"][0]
        
        # Verificar que ambos cambios se aplicaron (atomicidad)
        assert len(pedido["productos"]) == 2
        assert pedido["total"] == nuevo_total


class TestEliminarPedido:
    def test_eliminar_pedido(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = eliminar_pedido(mock_coleccion, cliente_id, "P001")
        assert resultado is True
        doc = mock_coleccion.find_one({"_id": cliente_id})
        assert len(doc["pedidos"]) == 0