"""Tests para los validadores chilenos."""
import pytest
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

    def test_rut_valido_con_guion(self):
        assert validar_rut("12345678-5") is True

    def test_rut_invalido_dv_incorrecto(self):
        assert validar_rut("12.345.678-0") is False

    def test_rut_con_k(self):
        # 16.666.666-K es matemáticamente válido (DV K = resto 10)
        assert validar_rut("16.666.666-K") is True

    def test_rut_con_k_minuscula(self):
        assert validar_rut("16666666k") is True

    def test_rut_vacio(self):
        assert validar_rut("") is False

    def test_rut_con_letras_invalidas(self):
        assert validar_rut("12.345.67A-5") is False

    def test_rut_muy_corto(self):
        assert validar_rut("123-5") is False

    def test_rut_muy_largo(self):
        assert validar_rut("123456789-5") is False

    def test_rut_con_espacios(self):
        assert validar_rut("  12.345.678-5  ") is True


class TestFormatearRUT:
    def test_formatear_rut_completo(self):
        assert formatear_rut("123456785") == "12.345.678-5"

    def test_formatear_rut_con_k(self):
        assert formatear_rut("16666666K") == "16.666.666-K"

    def test_formatear_rut_ya_formateado(self):
        assert formatear_rut("12.345.678-5") == "12.345.678-5"

    def test_formatear_rut_corto(self):
        assert formatear_rut("1234567-8") == "1.234.567-8"

    def test_formatear_rut_con_espacios(self):
        assert formatear_rut("  123456785  ") == "12.345.678-5"


class TestValidarTexto:
    def test_texto_valido(self):
        assert validar_texto_alfabetico("Juan Pérez") is True

    def test_texto_con_tildes(self):
        assert validar_texto_alfabetico("María José") is True

    def test_texto_con_ene(self):
        assert validar_texto_alfabetico("Ñoño") is True

    def test_texto_con_numeros(self):
        assert validar_texto_alfabetico("Juan123") is False

    def test_texto_vacio(self):
        assert validar_texto_alfabetico("") is False

    def test_texto_con_especiales(self):
        assert validar_texto_alfabetico("Juan@") is False


class TestValidarEmail:
    def test_email_valido(self):
        assert validar_email("juan@example.com") is True

    def test_email_con_subdominio(self):
        assert validar_email("juan@mail.example.com") is True

    def test_email_invalido_sin_arroba(self):
        assert validar_email("juanexample.com") is False

    def test_email_invalido_sin_dominio(self):
        assert validar_email("juan@") is False

    def test_email_invalido_sin_usuario(self):
        assert validar_email("@example.com") is False


class TestValidarTelefono:
    def test_telefono_valido(self):
        assert validar_telefono("+56912345678") is True

    def test_telefono_invalido_corto(self):
        assert validar_telefono("+56912345") is False

    def test_telefono_invalido_sin_prefijo(self):
        assert validar_telefono("912345678") is False

    def test_telefono_invalido_con_letras(self):
        assert validar_telefono("+5691234abcd") is False