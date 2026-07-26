"""Tests para los formatters."""
from src.ui.formatters import formatear_precio, generar_regex_con_tildes

class TestFormatearPrecio:
    def test_precio_entero(self):
        assert formatear_precio(25000) == "$25.000"

    def test_precio_grande(self):
        assert formatear_precio(1234567) == "$1.234.567"

    def test_precio_cero(self):
        assert formatear_precio(0) == "$0"

    def test_precio_decimal(self):
        # Usamos .51 para forzar el redondeo hacia arriba y evitar el banker's rounding
        assert formatear_precio(25000.51) == "$25.001"

    def test_precio_string_numerico(self):
        assert formatear_precio("25000") == "$25.000"

    def test_precio_invalido(self):
        assert formatear_precio("abc") == "$abc"

class TestGenerarRegex:
    def test_regex_simple(self):
        patron = generar_regex_con_tildes("maria")
        assert "m" in patron
        assert "[aáAÁ]" in patron

    def test_regex_con_n(self):
        patron = generar_regex_con_tildes("nunoa")
        assert "[nñNÑ]" in patron

    def test_regex_escape_caracteres_especiales(self):
        patron = generar_regex_con_tildes("test.+*")
        assert "\\." in patron or "\\+" in patron