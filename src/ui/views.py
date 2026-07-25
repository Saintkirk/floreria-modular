"""
Vistas de la interfaz de consola (UI Layer).
Gestiona la interacción con el usuario, validación de inputs y formato de salida.
No contiene lógica de base de datos directa; delega eso a los Services.
"""
import re
from datetime import datetime
from pymongo.collection import Collection
from src.config import (
    CATEGORIAS, ESTADOS_PEDIDO, OCASIONES,
    MAX_NOMBRE, MAX_RUT, MAX_EMAIL, MAX_TELEFONO,
    MAX_CALLE, MAX_NUMERO, MAX_COMUNA, MAX_NOTAS, MAX_EDAD_ANIOS
)
from src.ui.colors import Colors
from src.ui.formatters import formatear_precio, generar_regex_con_tildes
from src.ui.menu import seleccionar_cliente, mostrar_documento_completo
from src.validators.chilean_validators import (
    validar_rut, formatear_rut, validar_texto_alfabetico,
    validar_email, validar_telefono
)
from src.services.client_service import (
    obtener_cliente_por_rut, crear_cliente as svc_crear_cliente,
    actualizar_campo, eliminar_cliente, mostrar_catalogo
)
from src.services.order_service import (
    agregar_pedido, actualizar_estado_pedido,
    agregar_producto_a_pedido, eliminar_pedido
)
from src.services.search_service import (
    buscar_por_regex, buscar_por_fechas, buscar_por_comparacion,
    buscar_elemmatch, generar_numero_pedido
)


# ═══════════════════════════════════════════════════════════════
# 1. CREATE
# ═══════════════════════════════════════════════════════════════
def vista_crear_cliente(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- REGISTRAR NUEVO CLIENTE ---{Colors.END}")
    print(f"{Colors.YELLOW}Escribe 'c' para cancelar o 'v' para volver.{Colors.END}")
    
    # Nombre
    while True:
        nombre = input("Nombre completo: ").strip()
        if nombre.lower() in ['c', 'v']: return
        if len(nombre) > MAX_NOMBRE or not nombre or not validar_texto_alfabetico(nombre) or len(nombre.split()) < 2:
            print(f"{Colors.RED} Inválido (Mín 2 palabras, solo letras, máx {MAX_NOMBRE} chars){Colors.END}"); continue
        break
        
    # RUT
    while True:
        rut_input = input("RUT (ej: 12.345.678-5): ").strip()
        if rut_input.lower() in ['c', 'v']: return
        if len(rut_input) > MAX_RUT or not validar_rut(rut_input):
            print(f"{Colors.RED}✗ RUT inválido{Colors.END}"); continue
        rut_formateado = formatear_rut(rut_input)
        if coleccion.find_one({"rut": rut_formateado}):
            print(f"{Colors.RED}✗ RUT ya registrado{Colors.END}"); continue
        break
        
    # Email
    while True:
        email = input("Email: ").strip()
        if email.lower() in ['c', 'v']: return
        if len(email) > MAX_EMAIL or not validar_email(email):
            print(f"{Colors.RED}✗ Email inválido{Colors.END}"); continue
        if coleccion.find_one({"email": email}):
            print(f"{Colors.RED}✗ Email ya registrado{Colors.END}"); continue
        break
        
    # Teléfono
    while True:
        telefono = input("Teléfono (+569...): ").strip()
        if telefono.lower() in ['c', 'v']: return
        if len(telefono) > MAX_TELEFONO or not validar_telefono(telefono):
            print(f"{Colors.RED}✗ Teléfono inválido{Colors.END}"); continue
        break
        
    # Dirección
    print(f"\n{Colors.YELLOW}Dirección:{Colors.END}")
    calle = input("Calle: ").strip()
    if calle.lower() in ['c', 'v'] or not calle or len(calle) > MAX_CALLE: return
    numero = input("Número: ").strip()
    if numero.lower() in ['c', 'v'] or not numero or len(numero) > MAX_NUMERO: return
    while True:
        comuna = input("Comuna: ").strip()
        if comuna.lower() in ['c', 'v']: return
        if not comuna or not validar_texto_alfabetico(comuna) or len(comuna) > MAX_COMUNA:
            print(f"{Colors.RED}✗ Comuna inválida{Colors.END}"); continue
        break
        
    # Cumpleaños
    while True:
        cumple = input("Fecha de cumpleaños (DD/MM/YYYY): ").strip()
        if cumple.lower() in ['c', 'v']: return
        try:
            fecha_cumple = datetime.strptime(cumple, "%d/%m/%Y")
            if fecha_cumple > datetime.now() or fecha_cumple.year < (datetime.now().year - MAX_EDAD_ANIOS):
                print(f"{Colors.RED}✗ Fecha fuera de rango{Colors.END}"); continue
            break
        except ValueError:
            print(f"{Colors.RED}✗ Formato inválido{Colors.END}")
            
    # Categoría
    for i, cat in enumerate(CATEGORIAS, 1): print(f"  {i}. {cat}")
    while True:
        cat_op = input("Categoría (1-3): ").strip()
        if cat_op.lower() in ['c', 'v']: return
        if cat_op in ["1", "2", "3"]:
            categoria = CATEGORIAS[int(cat_op) - 1]; break
        print(f"{Colors.RED}✗ Opción inválida{Colors.END}")
        
    notas = input("Notas (Enter para omitir): ").strip()
    if len(notas) > MAX_NOTAS: notas = notas[:MAX_NOTAS]
    
    # Pedidos
    pedidos = []
    db = coleccion.database
    if input("\n¿Registrar pedido inicial? (s/n): ").strip().lower() == "s":
        for i, oc in enumerate(OCASIONES, 1): print(f"  {i}. {oc}")
        oc_op = input("Ocasión (1-6): ").strip()
        if oc_op not in [str(x) for x in range(1, 7)]: return
        ocasion = OCASIONES[int(oc_op) - 1]
        productos = []
        catalogo = mostrar_catalogo(db)
        while True:
            sel = input("Producto (número o 'listo'): ").strip()
            if sel.lower() == "listo": break
            try:
                num_prod = int(sel)
                if 1 <= num_prod <= len(catalogo):
                    prod_sel = catalogo[num_prod - 1]
                    cant = int(input(f"Cantidad para '{prod_sel['nombre']}': ").strip())
                    if cant > 0:
                        productos.append({"nombre": prod_sel['nombre'], "cantidad": cant, "precio": prod_sel['precio_base']})
            except ValueError: continue
        if productos:
            total = sum(p["cantidad"] * p["precio"] for p in productos)
            pedidos.append({
                "numero_pedido": generar_numero_pedido(coleccion), "fecha_pedido": datetime.now(),
                "ocasion": ocasion, "productos": productos, "total": total, "estado": "Pendiente"
            })
            
    documento = {
        "nombre": nombre, "rut": rut_formateado, "email": email, "telefono": telefono,
        "direccion": {"calle": calle, "numero": numero, "comuna": comuna},
        "fecha_registro": datetime.now(), "fecha_cumpleanos": fecha_cumple,
        "categoria_cliente": categoria, "notas": notas, "activo": True, "pedidos": pedidos
    }
    if svc_crear_cliente(coleccion, documento):
        print(f"{Colors.GREEN}✓ Cliente registrado exitosamente{Colors.END}")


# ══════════════════════════════════════════════════════════════
# 2. READ BÁSICO
# ═══════════════════════════════════════════════════════════════
def vista_listar_clientes(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- TODOS LOS CLIENTES ---{Colors.END}")
    clientes = list(coleccion.find({}, {"nombre": 1, "rut": 1, "categoria_cliente": 1, "activo": 1, "pedidos": 1, "fecha_registro": 1, "direccion.comuna": 1}))
    if not clientes: 
        print(f"{Colors.YELLOW}Sin clientes{Colors.END}")
        return
    for idx, c in enumerate(clientes, 1):
        estado = "Activo" if c.get('activo', True) else "Inactivo"
        n_pedidos = len(c.get('pedidos', []))
        total_gastado = sum(p.get('total', 0) for p in c.get('pedidos', []))
        fecha_str = c.get('fecha_registro').strftime('%d/%m/%Y') if c.get('fecha_registro') else 'N/A'
        print(f"\n{Colors.CYAN}{idx}. {c['nombre']}{Colors.END} | RUT: {c.get('rut')} | {c.get('categoria_cliente')} | {estado}")
        print(f"   Comuna: {c.get('direccion', {}).get('comuna')} | Registrado: {fecha_str} | Pedidos: {n_pedidos} | Gastado: {formatear_precio(total_gastado)}")
        if idx % 10 == 0 and idx != len(clientes):
            input(f"\n{Colors.YELLOW}--- Mostrados {idx} de {len(clientes)}. Enter para continuar ---{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# 3, 4, 5, 6. READ AVANZADO
# ═══════════════════════════════════════════════════════════════
def vista_buscar_simple(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- BÚSQUEDA POR COMPARACIÓN ---{Colors.END}")
    print("1. Total pedido  2. Precio producto  3. Cantidad  c. Cancelar")
    op = input("Elige: ").strip().lower()
    if op in ['c', 'v']: return
    campos = {"1": ("pedidos.total", float), "2": ("pedidos.productos.precio", float), "3": ("pedidos.productos.cantidad", int)}
    if op not in campos: return
    ruta, tipo = campos[op]
    print("1. $gt  2. $lt  3. $gte  4. $lte  5. $ne  6. $in")
    op_cond = input("Operador (1-6): ").strip()
    ops = {"1": "$gt", "2": "$lt", "3": "$gte", "4": "$lte", "5": "$ne", "6": "$in"}
    if op_cond not in ops: return
    try:
        val = [tipo(v.strip()) for v in input("Valor(es) (coma si es $in): ").split(",")] if ops[op_cond] == "$in" else tipo(input("Valor: ").strip())
    except ValueError: 
        print(f"{Colors.RED} Valor inválido{Colors.END}")
        return
    resultados = buscar_por_comparacion(coleccion, ruta, ops[op_cond], val)
    print(f"\n{Colors.GREEN}✓ {len(resultados)} encontrado(s){Colors.END}")
    for c in resultados: print(f"  • {c['nombre']} ({c.get('rut')})")

def vista_buscar_regex(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- BÚSQUEDA POR TEXTO PARCIAL ---{Colors.END}")
    print("1. Nombre  2. Email  3. Producto  c. Cancelar")
    op = input("Elige: ").strip().lower()
    if op in ['c', 'v']: return
    campos = {"1": "nombre", "2": "email", "3": "pedidos.productos.nombre"}
    if op not in campos: return
    patron = input("Patrón de búsqueda: ").strip()
    if not patron: return
    resultados = buscar_por_regex(coleccion, campos[op], patron)
    print(f"\n{Colors.GREEN}✓ {len(resultados)} resultado(s){Colors.END}")
    for c in resultados: print(f"  • {c['nombre']} ({c.get('email', 'N/A')})")

def vista_buscar_fechas(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- BUSCAR POR RANGO DE FECHAS ---{Colors.END}")
    try:
        fi = input("Fecha inicio (DD/MM/YYYY): ").strip()
        ff = input("Fecha fin (DD/MM/YYYY): ").strip()
        fecha_inicio = datetime.strptime(fi, "%d/%m/%Y")
        fecha_fin = datetime.strptime(ff, "%d/%m/%Y")
        if fecha_inicio > fecha_fin: 
            print(f"{Colors.RED}✗ Fechas invertidas{Colors.END}")
            return
        resultados = buscar_por_fechas(coleccion, fecha_inicio, fecha_fin)
        print(f"\n{Colors.GREEN}✓ {len(resultados)} cliente(s) con pedidos en el rango:{Colors.END}")
        for c in resultados:
            for p in c.get('pedidos', []):
                if fecha_inicio <= p.get('fecha_pedido', datetime.min) <= fecha_fin.replace(hour=23, minute=59, second=59):
                    print(f"  • {c['nombre']} - {p['numero_pedido']} - {formatear_precio(p['total'])}")
    except ValueError: 
        print(f"{Colors.RED}✗ Formato inválido{Colors.END}")

def vista_buscar_subdocumento(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- BUSCAR EN SUBDOCUMENTO/ARRAY ---{Colors.END}")
    print("1. Comuna  2. Ocasión  3. Estado  4. Rango Total ($elemMatch)  c. Cancelar")
    op = input("Elige: ").strip().lower()
    if op in ['c', 'v']: return
    if op == "1":
        patron = input("Texto de comuna: ").strip()
        resultados = buscar_por_regex(coleccion, "direccion.comuna", patron)
    elif op == "2":
        for i, oc in enumerate(OCASIONES, 1): print(f"  {i}. {oc}")
        resultados = list(coleccion.find({"pedidos.ocasion": OCASIONES[int(input("Ocasión (1-6): ").strip()) - 1]}))
    elif op == "3":
        for i, est in enumerate(ESTADOS_PEDIDO, 1): print(f"  {i}. {est}")
        resultados = list(coleccion.find({"pedidos.estado": ESTADOS_PEDIDO[int(input("Estado (1-4): ").strip()) - 1]}))
    elif op == "4":
        pmin, pmax = float(input("Mín: ")), float(input("Máx: "))
        resultados = buscar_elemmatch(coleccion, pmin, pmax)
    else: return
    print(f"\n{Colors.GREEN}✓ {len(resultados)} resultado(s){Colors.END}")
    for c in resultados: print(f"  • {c['nombre']}")


# ══════════════════════════════════════════════════════════════
# 7, 8. UPDATE
# ═══════════════════════════════════════════════════════════════
def vista_actualizar_raiz(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- ACTUALIZAR DATOS DEL CLIENTE ---{Colors.END}")
    cliente = seleccionar_cliente(coleccion, "actualizar datos")
    if not cliente: return
    cliente_id = cliente["_id"]
    mostrar_documento_completo(coleccion, cliente_id, "ANTES")
    print("1. Nombre  2. Email  3. Teléfono  4. Categoría  5. Calle  6. Comuna  7. Estado  8. Notas  c. Cancelar")
    op = input("Elige: ").strip().lower()
    if op in ['c', 'v']: return
    doc = coleccion.find_one({"_id": cliente_id})
    campo, valor = None, None
    if op == "1":
        val = input(f"Nuevo nombre (Actual: {doc.get('nombre')}): ").strip()
        if validar_texto_alfabetico(val) and len(val.split()) >= 2: campo, valor = "nombre", val
    elif op == "2":
        val = input("Nuevo email: ").strip()
        if validar_email(val): campo, valor = "email", val
    elif op == "3":
        val = input("Nuevo teléfono: ").strip()
        if validar_telefono(val): campo, valor = "telefono", val
    elif op == "4":
        for i, cat in enumerate(CATEGORIAS, 1): print(f"  {i}. {cat}")
        valor = CATEGORIAS[int(input("Categoría (1-3): ").strip()) - 1]; campo = "categoria_cliente"
    elif op in ["5", "6"]:
        val = input(f"Nueva {'calle' if op=='5' else 'comuna'}: ").strip()
        if val: campo, valor = f"direccion.{'calle' if op=='5' else 'comuna'}", val
    elif op == "7":
        valor = not doc.get('activo', True); campo = "activo"
    elif op == "8":
        valor = input("Nuevas notas: ").strip(); campo = "notas"
    if campo and actualizar_campo(coleccion, cliente_id, campo, valor):
        print(f"{Colors.GREEN}✓ Actualizado{Colors.END}")
        mostrar_documento_completo(coleccion, cliente_id, "DESPUÉS")
    else: print(f"{Colors.RED}✗ Datos inválidos{Colors.END}")

def vista_actualizar_subdocumento(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- ACTUALIZAR PEDIDOS ---{Colors.END}")
    cliente = seleccionar_cliente(coleccion, "gestionar pedidos")
    if not cliente: return
    cliente_id = cliente["_id"]
    mostrar_documento_completo(coleccion, cliente_id, "ANTES")
    print("1. Agregar pedido  2. Cambiar estado  3. Agregar producto  4. Cambiar precio  c. Cancelar")
    op = input("Elige: ").strip().lower()
    if op in ['c', 'v']: return
    cliente_doc = coleccion.find_one({"_id": cliente_id})
    pedidos = cliente_doc.get('pedidos', [])
    if op == "1":
        for i, oc in enumerate(OCASIONES, 1): print(f"  {i}. {oc}")
        ocasion = OCASIONES[int(input("Ocasión (1-6): ").strip()) - 1]
        catalogo = mostrar_catalogo(coleccion.database)
        num_prod = int(input("Producto del catálogo: ").strip())
        cant = int(input("Cantidad: ").strip())
        prod_sel = catalogo[num_prod - 1]
        total = cant * prod_sel['precio_base']
        nuevo_pedido = {"numero_pedido": generar_numero_pedido(coleccion), "fecha_pedido": datetime.now(), "ocasion": ocasion, "productos": [{"nombre": prod_sel['nombre'], "cantidad": cant, "precio": prod_sel['precio_base']}], "total": total, "estado": "Pendiente"}
        if agregar_pedido(coleccion, cliente_id, nuevo_pedido): print(f"{Colors.GREEN}✓ Pedido agregado{Colors.END}")
    elif op in ["2", "3", "4"] and pedidos:
        for i, p in enumerate(pedidos, 1): print(f"  {i}. {p['numero_pedido']} - {formatear_precio(p['total'])}")
        idx = int(input("N° pedido: ").strip()) - 1
        pedido = pedidos[idx]
        if op == "2":
            for i, est in enumerate(ESTADOS_PEDIDO, 1): print(f"  {i}. {est}")
            nuevo_estado = ESTADOS_PEDIDO[int(input("Estado (1-4): ").strip()) - 1]
            if actualizar_estado_pedido(coleccion, cliente_id, pedido['numero_pedido'], nuevo_estado): print(f"{Colors.GREEN}✓ Estado actualizado{Colors.END}")
        elif op == "3":
            catalogo = mostrar_catalogo(coleccion.database)
            num_prod = int(input("Producto: ").strip())
            cant = int(input("Cantidad: ").strip())
            prod_sel = catalogo[num_prod - 1]
            nuevo_total = pedido['total'] + (cant * prod_sel['precio_base'])
            if agregar_producto_a_pedido(coleccion, cliente_id, pedido['numero_pedido'], {"nombre": prod_sel['nombre'], "cantidad": cant, "precio": prod_sel['precio_base']}, nuevo_total): print(f"{Colors.GREEN}✓ Producto agregado{Colors.END}")
        elif op == "4":
            for i, pr in enumerate(pedido.get('productos', []), 1): print(f"  {i}. {pr['nombre']} - {formatear_precio(pr['precio'])}")
            pidx = int(input("N° producto: ").strip()) - 1
            nuevo_prec = float(input("Nuevo precio: ").strip())
            prod = pedido['productos'][pidx]
            nuevo_total = pedido['total'] - (prod['cantidad'] * prod['precio']) + (prod['cantidad'] * nuevo_prec)
            coleccion.update_one({"_id": cliente_id, "pedidos.numero_pedido": pedido['numero_pedido']}, {"$set": {f"pedidos.$.productos.{pidx}.precio": nuevo_prec, "pedidos.$.total": nuevo_total}})
            print(f"{Colors.GREEN}✓ Precio actualizado{Colors.END}")
    mostrar_documento_completo(coleccion, cliente_id, "DESPUÉS")


# ═══════════════════════════════════════════════════════════════
# 9. DELETE
# ═══════════════════════════════════════════════════════════════
def vista_eliminar(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- ELIMINAR ---{Colors.END}")
    print("1. Cliente por RUT  2. Por categoría  3. Inactivos  4. Pedido  c. Cancelar")
    op = input("Elige: ").strip().lower()
    if op in ['c', 'v']: return
    if op == "1":
        rut = input("RUT a eliminar: ").strip()
        cliente = obtener_cliente_por_rut(coleccion, rut)
        if not cliente: 
            print(f"{Colors.RED}✗ No encontrado{Colors.END}")
            return
        mostrar_documento_completo(coleccion, cliente["_id"], "A ELIMINAR")
        if input("¿Confirmas? (s/n): ").strip().lower() == "s":
            coleccion.delete_one({"rut": cliente["rut"]})
            print(f"{Colors.GREEN}✓ Eliminado{Colors.END}")
    elif op in ["2", "3"]:
        filtro = {"categoria_cliente": CATEGORIAS[int(input("Categoría (1-3): ").strip()) - 1]} if op == "2" else {"activo": False}
        docs = list(coleccion.find(filtro))
        if not docs: 
            print(f"{Colors.YELLOW}No hay{Colors.END}")
            return
        for d in docs: print(f"  • {d['nombre']} ({d['rut']})")
        if input(f"¿Eliminar {len(docs)}? (s/n): ").strip().lower() == "s":
            r = coleccion.delete_many({"_id": {"$in": [d["_id"] for d in docs]}})
            print(f"{Colors.GREEN}✓ {r.deleted_count} eliminado(s){Colors.END}")
    elif op == "4":
        cliente = seleccionar_cliente(coleccion, "eliminar pedido")
        if not cliente: return
        pedidos = coleccion.find_one({"_id": cliente["_id"]}).get('pedidos', [])
        for i, p in enumerate(pedidos, 1): print(f"  {i}. {p['numero_pedido']}")
        idx = int(input("N° pedido: ").strip()) - 1
        if eliminar_pedido(coleccion, cliente["_id"], pedidos[idx]['numero_pedido']):
            print(f"{Colors.GREEN}✓ Pedido eliminado{Colors.END}")


# ═══════════════════════════════════════════════════════════════
# 10, 11. EXTRAS
# ═══════════════════════════════════════════════════════════════
def vista_buscar_rut(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}--- BÚSQUEDA POR RUT ---{Colors.END}")
    rut = input("RUT: ").strip()
    if not validar_rut(rut): 
        print(f"{Colors.RED}✗ RUT inválido{Colors.END}")
        return
    cliente = obtener_cliente_por_rut(coleccion, rut)
    if cliente: mostrar_documento_completo(coleccion, cliente["_id"], "ENCONTRADO")
    else: print(f"{Colors.RED}✗ No encontrado{Colors.END}")

def vista_estadisticas(coleccion: Collection) -> None:
    print(f"\n{Colors.BOLD}=== 📊 ESTADÍSTICAS ==={Colors.END}")
    total = coleccion.count_documents({})
    activos = coleccion.count_documents({"activo": True})
    print(f"Clientes: {Colors.CYAN}{total}{Colors.END} (Activos: {Colors.GREEN}{activos}{Colors.END})")
    finanzas = list(coleccion.aggregate([
        {"$unwind": "$pedidos"},
        {"$group": {"_id": None, "total": {"$sum": "$pedidos.total"}, "prom": {"$avg": "$pedidos.total"}}}
    ]))
    if finanzas:
        f = finanzas[0]
        print(f"Ingresos: {Colors.GREEN}{formatear_precio(f['total'])}{Colors.END} | Ticket: {formatear_precio(f['prom'])}")