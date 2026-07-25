#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema CRUD Florería INACAP - Entry Point
Evaluación Integradora N°3 - TI3V32 | INACAP Puente Alto
Integrantes: Nazareth Arias, Leandro Parrao
"""
from src.database.connection import conectar_mongo
from src.ui.menu import mostrar_menu, esperar_y_volver
from src.ui.colors import Colors

# Importación perezosa (Lazy Loading) de las vistas para mejorar el tiempo de arranque
def _get_views():
    from src.ui import views
    return views

def main() -> None:
    """Punto de entrada principal del sistema."""
    coleccion = conectar_mongo()
    if coleccion is None:
        return
    views = _get_views()
    while True:
        mostrar_menu()
        opcion = input(f"\n{Colors.BOLD}Elige opción: {Colors.END}").strip()
        if opcion == "0":
            print(f"\n{Colors.GREEN}✓ Saliendo del sistema{Colors.END}")
            break
        # Mapeo de opciones a funciones de vista
        acciones = {
            "1": views.vista_crear_cliente,
            "2": views.vista_listar_clientes,
            "3": views.vista_buscar_simple,
            "4": views.vista_buscar_regex,
            "5": views.vista_buscar_fechas,
            "6": views.vista_buscar_subdocumento,
            "7": views.vista_actualizar_raiz,
            "8": views.vista_actualizar_subdocumento,
            "9": views.vista_eliminar,
            "10": views.vista_buscar_rut,
        }
        if opcion in acciones:
            acciones[opcion](coleccion)
            esperar_y_volver()
        elif opcion == "11":
            views.vista_estadisticas(coleccion)
            input(f"\n{Colors.YELLOW}Presione Enter para volver...{Colors.END}")
        else:
            print(f"{Colors.RED}✗ Opción inválida{Colors.END}")

if __name__ == "__main__":
    main()