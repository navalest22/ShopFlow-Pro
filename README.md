# ShopFlow Pro — Gestión de comercio electrónico

Aplicación de escritorio académica desarrollada en Python + Tkinter. La lógica está separada en capas y las estructuras de datos principales son implementaciones propias.

## Requisitos y ejecución
- Python 3.10 o superior.
- Tkinter (incluido normalmente en Python para Windows).
- ReportLab solo para comprobantes PDF.

```bash
python -m pip install -r requirements.txt
python app.py
```

Primer acceso:
- Usuario: `admin`
- Contraseña: `ShopFlow2026*`

**Cambia o crea credenciales propias para una demostración real.** El prototipo inicial crea un administrador por defecto cuando no hay usuarios.

## Pruebas automatizadas
```bash
python -m unittest discover -s tests -v
```

## Funcionalidades
1. Catálogo: crear, editar, eliminar (con validación de referencias), búsqueda exacta AVL.
2. Carrito: agregar, quitar, cambiar cantidades, deshacer y rehacer con pilas LIFO.
3. Pedidos: confirmación, reserva de inventario, cola FIFO, procesamiento simulado, detalle, búsqueda y cancelación de pedidos pendientes con reintegro de stock.
4. Inventario: movimientos auditables de entrada, salida, reserva y reintegro.
5. Dashboard: productos, unidades disponibles, pedidos, ventas pagadas, cancelaciones y ticket promedio.
6. Clientes: registro automático al crear pedido y consulta del directorio.
7. Comprobantes: generación PDF por pedido.
8. Exportación: pedidos y productos a CSV compatible con Excel.
9. Promociones: códigos de descuento porcentuales activos/inactivos.
10. Usuarios: login, hash PBKDF2 de contraseñas y roles ADMIN, INVENTARIO y VENTAS.

## Arquitectura
- `domain/`: modelos del dominio.
- `structures/`: árbol AVL, pila y cola enlazada.
- `repositories/`: persistencia JSON con escritura atómica.
- `services/`: reglas de negocio, catálogo, carrito, checkout, clientes, promociones, usuarios y reportes.
- `ui/`: interfaz Tkinter.
- `tests/`: pruebas automatizadas.
- `data/shopflow.json`: datos persistentes (se crea al iniciar).

## Reglas importantes
- El stock se reserva cuando se confirma el pedido y entra a la cola FIFO.
- Solo se pueden cancelar pedidos pendientes; al cancelar se reintegra el stock y se registra el movimiento.
- Los pedidos pagados no se pueden cancelar desde esta versión.
- Los precios y nombres de los artículos quedan congelados dentro del pedido para conservar el comprobante histórico.
- La búsqueda AVL es exacta por nombre normalizado; no es una búsqueda parcial.
- El pago es una simulación académica. No se conecta a bancos ni procesa dinero real.

## Limitaciones conocidas
- Persistencia local en un único archivo JSON: adecuada para demostración de escritorio, no para múltiples procesos o clientes concurrentes en producción.
- No hay pasarela de pago real ni autenticación remota.
- Los roles son permisos básicos de interfaz; la seguridad de producción requeriría backend, base de datos, gestión de sesiones y controles adicionales.
- El administrador inicial usa credenciales de demostración; cámbialas antes de presentar el proyecto.
