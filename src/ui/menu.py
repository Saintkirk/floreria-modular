"""
Menú principal y funciones de navegación del sistema.
"""
import os
from datetime import datetime
from typing import Optional
from pymongo.collection import Collection
from src.ui.colors import Colors
from src.ui.formatters import formatear_precio

def mostrar_menu() -> None:
    """Muestra el menú principal del sistema."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{Colors.BOLD}{Colors.HEADER}=== FLORERÍA INACAP - GESTIÓN DE CLIENTES ==={Colors.END}")
    print(f"{Colors.CYAN}1. Registrar nuevo cliente{Colors.END}")
    print(f"{Colors.CYAN}2. Listar todos los clientes{Colors.END}")
    print(f"{Colors.CYAN}3. Buscar por comparación de valores{Colors.END}")
    print(f"{Colors.CYAN}4. Buscar por texto parcial (nombre, email o producto){Colors.END}")
    print(f"{Colors.CYAN}5. Buscar pedidos por rango de fechas{Colors.END}")
    print(f"{Colors.CYAN}6. Buscar por comuna, ocasión o estado de pedido{Colors.END}")
    print(f"{Colors.CYAN}7. Actualizar datos del cliente{Colors.END}")
    print(f"{Colors.CYAN}8. Actualizar pedidos del cliente{Colors.END}")
    print(f"{Colors.CYAN}9. Eliminar cliente o pedido{Colors.END}")
    print(f"{Colors.CYAN}10. Buscar cliente directo por RUT{Colors.END}")
    print(f"{Colors.CYAN}11. Ver estadísticas del sistema{Colors.END}")
    print(f"{Colors.CYAN}0. Salir del sistema{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}=============================================={Colors.END}")

def esperar_y_volver() -> None:
    """Menú de pausa tras cada operación."""
    while True:
        print(f"\n{Colors.YELLOW}1. Volver al menú principal{Colors.END}")
        print(f"{Colors.YELLOW}2. Salir del sistema{Colors.END}")
        opcion = input(f"{Colors.BOLD}Seleccione (1/2, c/v para volver): {Colors.END}").strip().lower()
        
        if opcion in ['2']:
            print(f"\n{Colors.GREEN}✓ Saliendo del sistema...{Colors.END}")
            exit()
        elif opcion in ['1', 'c', 'v']:
            return
        else:
            print(f"{Colors.RED}✗ Opción inválida. Use 1, 2, c o v{Colors.END}")

def seleccionar_cliente(coleccion: Collection, accion: str = "operar") -> Optional[dict]:
    """
    Muestra lista numerada de clientes y permite seleccionar uno.
    
    Args:
        coleccion: Colección de MongoDB.
        accion: Texto descriptivo de la acción a realizar.
    
    Returns:
        Diccionario del cliente seleccionado o None si se cancela.
    """
    clientes = list(coleccion.find({}, {"nombre": 1, "rut": 1, "categoria_cliente": 1, "activo": 1}))
    
    if not clientes:
        print(f"{Colors.YELLOW}No hay clientes registrados.{Colors.END}")
        return None
    
    print(f"\n{Colors.YELLOW}Clientes disponibles:{Colors.END}")
    for idx, c in enumerate(clientes, 1):
        estado = "✓" if c.get('activo', True) else "✗ Inactivo"
        print(f"  {Colors.CYAN}{idx}.{Colors.END} {c['nombre']} ({c['rut']}) [{c.get('categoria_cliente','N/A')}] {estado}")
    
    print(f"  {Colors.CYAN}c.{Colors.END} Cancelar / {Colors.CYAN}v.{Colors.END} Volver")
    
    while True:
        try:
            opcion = input(f"\n{Colors.BOLD}Elige cliente para {accion} (1-{len(clientes)}, c/v para salir): {Colors.END}").strip().lower()
            
            if opcion in ["c", "v"]:
                print(f"{Colors.YELLOW}Operación cancelada.{Colors.END}")
                return None
            
            idx = int(opcion)
            if 1 <= idx <= len(clientes):
                return clientes[idx - 1]
            else:
                print(f"{Colors.RED}✗ Número fuera de rango{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}✗ Ingresa un número válido, o 'c' para cancelar{Colors.END}")

def mostrar_documento_completo(coleccion: Collection, cliente_id, titulo: str = "") -> None:
    """
    Muestra un resumen estructurado del documento completo.
    Utilizado para mostrar el estado antes/después de modificaciones.
    
    Args:
        coleccion: Colección de MongoDB.
        cliente_id: ObjectId del cliente.
        titulo: Título descriptivo para el encabezado.
    """
    doc = coleccion.find_one({"_id": cliente_id})
    
    if not doc:
        print(f"{Colors.RED}✗ Documento no encontrado{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}{'='*20} {titulo} {'='*20}{Colors.END}")
    print(f"{Colors.CYAN}Nombre:{Colors.END} {doc.get('nombre')}")
    print(f"{Colors.CYAN}RUT:{Colors.END} {doc.get('rut')}")
    print(f"{Colors.CYAN}Email:{Colors.END} {doc.get('email')}")
    print(f"{Colors.CYAN}Teléfono:{Colors.END} {doc.get('telefono')}")
    print(f"{Colors.CYAN}Categoría:{Colors.END} {doc.get('categoria_cliente')}")
    print(f"{Colors.CYAN}Estado:{Colors.END} {'Activo' if doc.get('activo') else 'Inactivo'}")
    
    dir_doc = doc.get('direccion', {})
    print(f"{Colors.CYAN}Dirección:{Colors.END} {dir_doc.get('calle')} {dir_doc.get('numero')}, {dir_doc.get('comuna')}")
    print(f"{Colors.CYAN}Notas:{Colors.END} {doc.get('notas', 'N/A')}")
    
    fecha_reg = doc.get('fecha_registro')
    fecha_cumple = doc.get('fecha_cumpleanos')
    
    # Manejo seguro de fechas
    if isinstance(fecha_reg, datetime):
        fecha_reg_str = fecha_reg.strftime('%d/%m/%Y')
    else:
        fecha_reg_str = str(fecha_reg) if fecha_reg else 'N/A'
    
    if isinstance(fecha_cumple, datetime):
        fecha_cumple_str = fecha_cumple.strftime('%d/%m/%Y')
    else:
        fecha_cumple_str = str(fecha_cumple) if fecha_cumple else 'N/A'
    
    print(f"{Colors.CYAN}Fecha registro:{Colors.END} {fecha_reg_str}")
    print(f"{Colors.CYAN}Cumpleaños:{Colors.END} {fecha_cumple_str}")
    
    print(f"\n{Colors.CYAN}Historial de Pedidos ({len(doc.get('pedidos', []))}):{Colors.END}")
    for p in doc.get('pedidos', []):
        print(f"   {Colors.BOLD}► {p['numero_pedido']}{Colors.END} ({p['ocasion']}) | Estado: {p['estado']} | Total: {formatear_precio(p['total'])}")
        
        productos_pedido = p.get('productos', [])
        if productos_pedido:
            print(f"     {Colors.YELLOW}Productos incluidos:{Colors.END}")
            for prod in productos_pedido:
                print(f"       • {prod['nombre']} - {prod['cantidad']} unidades - {formatear_precio(prod['precio'])}")
        else:
            print(f"     {Colors.YELLOW}Sin productos{Colors.END}")
    
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")