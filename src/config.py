"""
Configuración centralizada del sistema.
Gestiona variables de entorno y constantes del dominio.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Base de datos ───────────────────────────────────────────
MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME: str = os.getenv("DB_NAME", "floreria_db")
COLLECTION_CLIENTS: str = "clientes"
COLLECTION_CATALOG: str = "productos_catalogo"

# ─── Constantes del dominio ──────────────────────────────────
CATEGORIAS: list[str] = ["Normal", "Premium", "VIP"]
ESTADOS_PEDIDO: list[str] = ["Pendiente", "En preparación", "Entregado", "Cancelado"]
OCASIONES: list[str] = [
    "Cumpleaños", "Aniversario", "Boda",
    "Duelo", "Día de la Madre", "Otra"
]

# ── Límites de validación ───────────────────────────────────
MAX_NOMBRE: int = 80
MAX_RUT: int = 12
MAX_EMAIL: int = 100
MAX_TELEFONO: int = 15
MAX_CALLE: int = 50
MAX_NUMERO: int = 10
MAX_COMUNA: int = 30
MAX_NOTAS: int = 300
MAX_EDAD_ANIOS: int = 100