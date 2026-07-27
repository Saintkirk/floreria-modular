"""Módulo de acceso a MongoDB."""
from pymongo import MongoClient
from typing import Optional
from src.config import MONGO_URI, DB_NAME

_db = None
_client = None

def get_database():
    """Obtiene la base de datos MongoDB."""
    global _db, _client
    if _db is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            _db = _client[DB_NAME]
        except Exception:
            # Fallback para tests o cuando no hay conexión
            _db = None
    return _db

def get_client():
    """Obtiene el cliente MongoDB."""
    return _client