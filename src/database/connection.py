"""
Gestión de conexión a MongoDB.
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.collection import Collection
from typing import Optional
from src.config import MONGO_URI, DB_NAME, COLLECTION_CLIENTS
from src.ui.colors import Colors

def conectar_mongo() -> Optional[Collection]:
    """
    Establece conexión con MongoDB y retorna la colección de clientes.
    Returns:
        Colección de MongoDB o None si la conexión falla.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[DB_NAME]
        coleccion = db[COLLECTION_CLIENTS]
        print(f"{Colors.GREEN}✓ Conexión a MongoDB exitosa{Colors.END}")
        return coleccion
    except (ConnectionFailure, ServerSelectionTimeoutError):
        print(f"{Colors.RED}✗ Error: No se pudo conectar a MongoDB{Colors.END}")
        return None

def obtener_db(coleccion: Collection):
    """Obtiene la referencia a la base de datos desde una colección."""
    return coleccion.database