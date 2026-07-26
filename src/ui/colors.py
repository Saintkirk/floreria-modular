"""
Códigos ANSI para colores en terminal.
Compatible con Windows mediante colorama.
"""
from colorama import init

init()

class Colors:
    """Paleta de colores ANSI para la interfaz de consola."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'