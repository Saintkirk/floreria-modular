"""
Funciones de formateo para visualización en consola.
Incluye formato de precios chilenos y regex con soporte de tildes.
"""
import re
from typing import Any

def formatear_precio(monto: Any) -> str:
    """
    Formatea un monto al formato chileno: $10.000
    Args:
        monto: Valor numérico a formatear.
    Returns:
        String formateado con separador de miles chileno.
    """
    try:
        return f"${float(monto):,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return f"${monto}"

def generar_regex_con_tildes(texto: str) -> str:
    """
    Convierte un texto en una expresión regular que ignora
    tildes, diacríticos y la letra ñ.
    Args:
        texto: Texto de búsqueda ingresado por el usuario.
    Returns:
        Patrón regex compatible con MongoDB $regex.
    """
    mapa: dict[str, str] = {
        'a': '[aáAÁ]', 'á': '[aáAÁ]', 'A': '[aáAÁ]', 'Á': '[aáAÁ]',
        'e': '[eéEÉ]', 'é': '[eéEÉ]', 'E': '[eéEÉ]', 'É': '[eéEÉ]',
        'i': '[iíIÍ]', 'í': '[iíIÍ]', 'I': '[iíIÍ]', 'Í': '[iíIÍ]',
        'o': '[oóOÓ]', 'ó': '[oóOÓ]', 'O': '[oóOÓ]', 'Ó': '[oóOÓ]',
        'u': '[uúUÚ]', 'ú': '[uúUÚ]', 'U': '[uúUÚ]', 'Ú': '[uúUÚ]',
        'n': '[nñNÑ]', 'ñ': '[nñNÑ]', 'N': '[nñNÑ]', 'Ñ': '[nñNÑ]',
    }
    return "".join(mapa.get(c, c) for c in texto)