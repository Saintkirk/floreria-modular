"""Tests para el servicio de búsquedas."""
import pytest
from datetime import datetime
from src.services.client_service import crear_cliente
from src.services.search_service import (
    buscar_por_regex,
    buscar_por_comparacion,
    buscar_pedidos_por_rango_total,
    buscar_por_fechas,
    generar_numero_pedido,
)


class TestBuscarPorRegex:
    def test_buscar_por_nombre(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultados = buscar_por_regex(mock_coleccion, "nombre", "Juan")
        assert len(resultados) == 1

    def test_buscar_con_tildes(self, mock_coleccion, cliente_ejemplo):
        cliente_ejemplo["nombre"] = "María José"
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultados = buscar_por_regex(mock_coleccion, "nombre", "Maria")
        assert len(resultados) == 1


class TestBuscarPorComparacion:
    def test_buscar_con_gt(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultados = buscar_por_comparacion(
            mock_coleccion, "pedidos.total", "$gt", 20000
        )
        assert len(resultados) == 1

    def test_buscar_con_operador_invalido(self, mock_coleccion, cliente_ejemplo):
        """Test de seguridad: operadores no permitidos deben rechazarse."""
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultados = buscar_por_comparacion(
            mock_coleccion, "pedidos.total", "$where", "malicioso"
        )
        assert len(resultados) == 0  # Debe retornar vacío por seguridad


class TestBuscarPedidosPorRangoTotal:
    def test_buscar_rango(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        resultados = buscar_pedidos_por_rango_total(mock_coleccion, 20000, 30000)
        assert len(resultados) == 1


class TestBuscarPorFechas:
    def test_buscar_rango_fechas(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        fecha_inicio = datetime(2024, 1, 1)
        fecha_fin = datetime(2024, 1, 31)
        resultados = buscar_por_fechas(mock_coleccion, fecha_inicio, fecha_fin)
        assert len(resultados) == 1


class TestGenerarNumeroPedido:
    def test_generar_primer_pedido(self, mock_coleccion):
        num = generar_numero_pedido(mock_coleccion)
        assert num == "P001"

    def test_generar_pedido_secuencial(self, mock_coleccion, cliente_ejemplo):
        crear_cliente(mock_coleccion, cliente_ejemplo)
        num = generar_numero_pedido(mock_coleccion)
        assert num == "P002"