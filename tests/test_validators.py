"""Tests para los validadores chilenos."""
from src.validators.chilean_validators import (
    validar_rut,
    formatear_rut,
    validar_texto_alfabetico,
    validar_email,
    validar_telefono,
)


class TestValidarRUT:
    def test_rut_valido_con_formato(self):
        assert validar_rut("12.345.678-5") is True

    def test_rut_valido_sin_formato(self):
        assert validar_rut("123456785") is True

    def test_rut_invalido(self):
        assert validar_rut("12.345.678-0") is False

    def test_rut_con_k(self):
        # 16.666.666-K es matemáticamente válido (DV K = resto 10)
        assert validar_rut("16.666.666-K") is True

    def test_rut_vacio(self):
        assert validar_rut("") is False


class TestFormatearRUT:
    def test_formatear_rut_completo(self):
        assert formatear_rut("123456785") == "12.345.678-5"

    def test_formatear_rut_con_k(self):
        assert formatear_rut("16666666K") == "16.666.666-K"


class TestValidarTexto:
    def test_texto_valido(self):
        assert validar_texto_alfabetico("Juan Pérez") is True

    def test_texto_con_numeros(self):
        assert validar_texto_alfabetico("Juan123") is False


class TestValidarEmail:
    def test_email_valido(self):
        assert validar_email("juan@example.com") is True

    def test_email_invalido(self):
        assert validar_email("juan@") is False


class TestValidarTelefono:
    def test_telefono_valido(self):
        assert validar_telefono("+56912345678") is True

    def test_telefono_invalido(self):
        assert validar_telefono("+56912345") is False