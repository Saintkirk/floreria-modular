"""Tests para el servicio de clientes."""
from src.services.client_service import (
    crear_cliente,
    actualizar_campo,
    eliminar_cliente,
)


class TestCrearCliente:
    def test_crear_cliente_exitoso(self, mock_coleccion, cliente_ejemplo):
        resultado = crear_cliente(mock_coleccion, cliente_ejemplo)
        assert resultado is not None
        assert mock_coleccion.count_documents({}) == 1

    def test_crear_cliente_vacio(self, mock_coleccion):
        resultado = crear_cliente(mock_coleccion, {})
        assert resultado is not None


class TestActualizarCampo:
    def test_actualizar_nombre(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = actualizar_campo(mock_coleccion, cliente_id, "nombre", "María López")
        assert resultado is True
        doc = mock_coleccion.find_one({"_id": cliente_id})
        assert doc["nombre"] == "María López"


class TestEliminarCliente:
    def test_eliminar_cliente(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = eliminar_cliente(mock_coleccion, cliente_id)
        assert resultado is True
        assert mock_coleccion.count_documents({}) == 0