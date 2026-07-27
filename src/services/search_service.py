"""
Servicio de búsquedas (lógica de negocio).
"""
import re
from typing import List, Dict, Any
from datetime import datetime
from pymongo.collection import Collection
from bson import ObjectId


def buscar_por_regex(coleccion: Collection, campo: str, texto: str) -> List[Dict[str, Any]]:
    """
    Busca documentos usando una expresión regular que ignora tildes.

    Args:
        coleccion: Colección de MongoDB.
        campo: Nombre del campo a buscar.
        texto: Texto a buscar.

    Returns:
        Lista de documentos encontrados.
    """
    # Generar patrón regex que ignora tildes y ñ
    patron = _generar_patron_regex(texto)
    try:
        query = {campo: {"$regex": patron, "$options": "i"}}
        resultados = list(coleccion.find(query))
        return resultados
    except Exception:
        return []


def _generar_patron_regex(texto: str) -> str:
    """Convierte un texto en una expresión regular que ignora tildes y ñ."""
    texto = re.escape(texto)

    mapa = {
        'a': '[aáAÁ]', 'á': '[aáAÁ]', 'A': '[aáAÁ]', 'Á': '[aáAÁ]',
        'e': '[eéEÉ]', 'é': '[eéEÉ]', 'E': '[eéEÉ]', 'É': '[eéEÉ]',
        'i': '[iíIÍ]', 'í': '[iíIÍ]', 'I': '[iíIÍ]', 'Í': '[iíIÍ]',
        'o': '[oóOÓ]', 'ó': '[oóOÓ]', 'O': '[oóOÓ]', 'Ó': '[oóOÓ]',
        'u': '[uúUÚ]', 'ú': '[uúUÚ]', 'U': '[uúUÚ]', 'Ú': '[uúUÚ]',
        'n': '[nñNÑ]', 'ñ': '[nñNÑ]', 'N': '[nñNÑ]', 'Ñ': '[nñNÑ]',
    }

    return "".join(mapa.get(c, c) for c in texto)


def buscar_por_comparacion(
    coleccion: Collection,
    campo: str,
    operador: str,
    valor: Any
) -> List[Dict[str, Any]]:
    """
    Busca documentos usando operadores de comparación.

    Args:
        coleccion: Colección de MongoDB.
        campo: Nombre del campo a comparar.
        operador: Operador de comparación ($gt, $lt, $gte, $lte, $eq, $ne).
        valor: Valor a comparar.

    Returns:
        Lista de documentos encontrados.
    """
    # Lista blanca de operadores permitidos por seguridad
    operadores_validos = {"$gt", "$lt", "$gte", "$lte", "$eq", "$ne"}

    if operador not in operadores_validos:
        return []

    try:
        query = {campo: {operador: valor}}
        resultados = list(coleccion.find(query))
        return resultados
    except Exception:
        return []


def buscar_pedidos_por_rango_total(
    coleccion: Collection,
    minimo: float,
    maximo: float
) -> List[Dict[str, Any]]:
    """
    Busca clientes con pedidos en un rango de total.

    Args:
        coleccion: Colección de MongoDB.
        minimo: Total mínimo del pedido.
        maximo: Total máximo del pedido.

    Returns:
        Lista de documentos encontrados.
    """
    try:
        query = {"pedidos.total": {"$gte": minimo, "$lte": maximo}}
        resultados = list(coleccion.find(query))
        return resultados
    except Exception:
        return []


def buscar_por_fechas(
    coleccion: Collection,
    fecha_inicio: datetime,
    fecha_fin: datetime
) -> List[Dict[str, Any]]:
    """
    Busca clientes con pedidos en un rango de fechas.

    Args:
        coleccion: Colección de MongoDB.
        fecha_inicio: Fecha de inicio del rango.
        fecha_fin: Fecha de fin del rango.

    Returns:
        Lista de documentos encontrados.
    """
    try:
        query = {"pedidos.fecha_pedido": {"$gte": fecha_inicio.strftime("%Y-%m-%d"), "$lte": fecha_fin.strftime("%Y-%m-%d")}}
        resultados = list(coleccion.find(query))
        return resultados
    except Exception:
        return []


def generar_numero_pedido(coleccion: Collection) -> str:
    """
    Genera el siguiente número de pedido secuencial.

    Args:
        coleccion: Colección de MongoDB.

    Returns:
        String con el número de pedido (ej: "P001").
    """
    try:
        # Buscar todos los pedidos existentes
        todos_los_clientes = coleccion.find({}, {"pedidos.numero_pedido": 1})

        numeros_existentes = []
        for cliente in todos_los_clientes:
            pedidos = cliente.get("pedidos", [])
            for pedido in pedidos:
                numero = pedido.get("numero_pedido", "")
                if numero.startswith("P"):
                    try:
                        num = int(numero[1:])
                        numeros_existentes.append(num)
                    except ValueError:
                        pass

        if not numeros_existentes:
            return "P001"

        siguiente_numero = max(numeros_existentes) + 1
        return f"P{siguiente_numero:03d}"
    except Exception:
        return "P001"