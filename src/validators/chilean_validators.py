"""
Validadores específicos para datos chilenos y formatos generales.
Incluye validación de RUT (módulo 11), teléfonos +569, emails y texto.
"""
import re

def validar_texto_alfabetico(texto: str) -> bool:
    """Valida que el texto contenga solo letras (incluye tildes) y espacios."""
    return re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", texto) is not None

def validar_email(email: str) -> bool:
    """Valida formato básico de email."""
    return re.match(r"^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$", email) is not None

def validar_telefono(telefono: str) -> bool:
    """Valida formato de teléfono chileno móvil: +569 + 8 dígitos."""
    return re.match(r"^\+569\d{8}$", telefono) is not None

def validar_rut(rut: str) -> bool:
    """
    Valida un RUT chileno usando el algoritmo módulo 11.
    Args:
        rut: RUT a validar (con o sin formato, con o sin guión).
    Returns:
        True si el RUT es válido, False en caso contrario.
    """
    rut = rut.replace(".", "").replace("-", "").upper().strip()
    if not re.match(r"^\d{7,8}[0-9K]$", rut):
        return False
    cuerpo = rut[:-1]
    dv = rut[-1]
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    resto = 11 - (suma % 11)
    if resto == 11:
        dv_esperado = "0"
    elif resto == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(resto)
    return dv == dv_esperado

def formatear_rut(rut: str) -> str:
    """
    Formatea un RUT al formato estándar XX.XXX.XXX-X.
    Args:
        rut: RUT sin formato o con formato parcial.
    Returns:
        RUT formateado.
    """
    rut = rut.replace(".", "").replace("-", "").upper().strip()
    cuerpo = rut[:-1]
    dv = rut[-1]
    cuerpo_formateado = ""
    for i, d in enumerate(reversed(cuerpo)):
        if i > 0 and i % 3 == 0:
            cuerpo_formateado = "." + cuerpo_formateado
        cuerpo_formateado = d + cuerpo_formateado
    return f"{cuerpo_formateado}-{dv}"