"""Tests para el servicio de clientes."""
import pytest
from src.services.client_service import (
    crear_cliente,
    actualizar_campo,
    eliminar_cliente,
    eliminar_cliente_por_rut,
    eliminar_clientes_por_filtro,
    obtener_cliente_por_rut,
    existe_rut,
    existe_email,
)


class TestCrearCliente:
    def test_crear_cliente_exitoso(self, mock_coleccion, cliente_ejemplo):
        resultado = crear_cliente(mock_coleccion, cliente_ejemplo)
        assert resultado is not None
        assert mock_coleccion.count_documents({}) == 1

    def test_crear_cliente_retorna_objectid(self, mock_coleccion, cliente_ejemplo):
        from bson import ObjectId
        resultado = crear_cliente(mock_coleccion, cliente_ejemplo)
        assert isinstance(resultado, ObjectId)

    def test_crear_cliente_vacio(self, mock_coleccion):
        # Con mongomock permite insertar documentos vacíos
        resultado = crear_cliente(mock_coleccion, {})
        assert resultado is not None


class TestObtenerClientePorRUT:
    def test_obtener_cliente_existente(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = obtener_cliente_por_rut(mock_coleccion, "12.345.678-5")
        assert resultado is not None
        assert resultado["nombre"] == "Juan Pérez"

    def test_obtener_cliente_no_existente(self, mock_coleccion):
        resultado = obtener_cliente_por_rut(mock_coleccion, "99.999.999-9")
        assert resultado is None


class TestExisteRUT:
    def test_rut_existe(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        assert existe_rut(mock_coleccion, "12.345.678-5") is True

    def test_rut_no_existe(self, mock_coleccion):
        assert existe_rut(mock_coleccion, "99.999.999-9") is False


class TestExisteEmail:
    def test_email_existe(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        assert existe_email(mock_coleccion, "juan@example.com") is True

    def test_email_no_existe(self, mock_coleccion):
        assert existe_email(mock_coleccion, "otro@example.com") is False


class TestActualizarCampo:
    def test_actualizar_nombre(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = actualizar_campo(mock_coleccion, cliente_id, "nombre", "María López")
        assert resultado is True
        doc = mock_coleccion.find_one({"_id": cliente_id})
        assert doc["nombre"] == "María López"

    def test_actualizar_campo_no_permitido(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        # Intentar actualizar _id debería fallar (no está en whitelist)
        resultado = actualizar_campo(mock_coleccion, cliente_id, "_id", "nuevo_id")
        assert resultado is False

    def test_actualizar_campo_inexistente(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = actualizar_campo(mock_coleccion, cliente_id, "rut", "99.999.999-9")
        assert resultado is False  # rut no está en whitelist


class TestEliminarCliente:
    def test_eliminar_cliente(self, mock_coleccion, cliente_ejemplo):
        cliente_id = crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = eliminar_cliente(mock_coleccion, cliente_id)
        assert resultado is True
        assert mock_coleccion.count_documents({}) == 0

    def test_eliminar_cliente_inexistente(self, mock_coleccion):
        from bson import ObjectId
        resultado = eliminar_cliente(mock_coleccion, ObjectId())
        assert resultado is False


class TestEliminarClientePorRUT:
    def test_eliminar_por_rut(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = eliminar_cliente_por_rut(mock_coleccion, "12.345.678-5")
        assert resultado is True
        assert mock_coleccion.count_documents({}) == 0


class TestEliminarClientesPorFiltro:
    def test_eliminar_por_categoria(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = eliminar_clientes_por_filtro(mock_coleccion, {"categoria_cliente": "Normal"})
        assert resultado == 1

    def test_eliminar_inactivos(self, mock_coleccion, cliente_ejemplo):
        cliente_ejemplo["activo"] = False
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultado = eliminar_clientes_por_filtro(mock_coleccion, {"activo": False})
        assert resultado == 1