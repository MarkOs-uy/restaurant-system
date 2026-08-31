# Functional Scope

## Objetivo

Este documento define el alcance funcional actual de Marcha.

Su propósito es dejar claro:

- qué funcionalidades forman parte del producto;
- qué áreas están actualmente soportadas;
- qué responsabilidades cubre cada módulo;
- qué funcionalidades todavía no forman parte del alcance.

Este documento describe el alcance funcional, no detalles de implementación.

---

# Alcance actual

Marcha cubre actualmente las siguientes áreas:

```text
autenticación
usuarios
mesas
pedidos
items
producción
estaciones
productos
categorías
pagos
caja
reportes
backups
configuración
licenciamiento
```

---

# Autenticación

Incluye:

- login;
- JWT;
- usuarios activos;
- roles;
- validación de restaurante;
- control de permisos.

Roles actuales:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

---

# Usuarios

Permite:

- crear usuarios;
- modificar usuarios;
- asignar roles;
- activar o desactivar cuando corresponde;
- asociar usuarios a un restaurante.

---

# Mesas

Permite:

- crear mesas;
- visualizar mesas;
- modificar configuración;
- representar estado;
- asociar pedidos;
- configurar layout.

---

# Layout

Permite organizar visualmente las mesas.

Incluye datos como:

```text
posición
dimensiones generales
grid
snap
forma
capacidad
```

según la implementación vigente.

---

# Pedidos

Permite:

- abrir pedido;
- agregar productos;
- modificar items pendientes;
- eliminar items pendientes;
- añadir notas;
- enviar productos;
- seguir estados;
- cancelar items cuando corresponde;
- aplicar descuentos;
- registrar pagos;
- cerrar pedido.

---

# Estados de Order

Estados actuales:

```text
OPEN
SENT
IN_PROGRESS
READY
CLOSED
CANCELLED
```

---

# Items

Permite:

- crear items;
- modificar cantidad mientras están pendientes;
- incluir notas;
- enviar a producción;
- cambiar estados;
- entregar;
- cancelar cuando corresponde.

---

# Estados de OrderItem

```text
PENDING
SENT
IN_PROGRESS
READY
DELIVERED
CANCELLED
```

---

# Producción

Permite:

- distribuir productos por estación;
- consultar items pendientes;
- iniciar producción;
- marcar productos preparados;
- sincronizar estados con salón.

---

# Estaciones

Permite:

- crear estaciones;
- modificar estaciones;
- activar;
- desactivar;
- asociar productos.

Las estaciones no se eliminan normalmente si existen referencias históricas.

---

# Categorías

Permite:

- crear;
- modificar;
- organizar productos.

---

# Productos

Permite:

- crear;
- editar;
- asignar precio;
- asociar categoría;
- asociar estación;
- activar o desactivar.

---

# Pagos

Permite registrar:

```text
CASH
CARD
TRANSFER
```

Una orden puede tener múltiples pagos.

---

# Descuentos

Permite aplicar descuentos respetando:

```text
discount <= subtotal
```

y evitando inconsistencias con pagos ya realizados.

---

# Caja

Incluye:

- apertura;
- importe inicial;
- pagos;
- movimientos;
- ventas;
- efectivo esperado;
- efectivo contado;
- diferencia;
- cierre.

---

# Movimientos de caja

Tipos actuales:

```text
cash_in
cash_out
```

Cada movimiento puede incluir:

- monto;
- motivo;
- usuario;
- fecha.

---

# Reportes

El sistema incluye reportes derivados de la información operativa.

Puede comprender:

- ventas;
- productos;
- medios de pago;
- tickets;
- períodos;
- caja.

El detalle exacto puede evolucionar sin modificar el núcleo operativo.

---

# Backups

Incluye:

- manual;
- automático;
- diario;
- semanal;
- mensual;
- retención;
- restore;
- pre-restore;
- descarga.

---

# Email de backups

Puede utilizar SMTP para envío de respaldos.

Esta funcionalidad es complementaria.

No forma parte del flujo crítico del restaurante.

---

# Configuración

Marcha almacena configuración persistente para funcionalidades como:

- backups;
- SMTP;
- scheduling;
- preferencias del sistema.

---

# Tiempo real

Incluye sincronización mediante WebSockets.

Áreas principales:

- órdenes;
- items;
- cocina;
- pagos;
- caja.

---

# Licenciamiento

Incluye:

- fingerprint;
- archivo de licencia;
- firma Ed25519;
- validación local;
- bloqueo de backend ante licencia inválida.

---

# Instalación

El producto incluye scripts para:

```text
instalar
iniciar
detener
actualizar
desinstalar
```

---

# Persistencia

Los datos de producción se almacenan en PostgreSQL.

La base de datos debe sobrevivir:

- reinicios;
- actualizaciones;
- recreación de contenedores;
- desinstalación normal.

---

# Fuera del alcance actual

No deben asumirse como funcionalidades existentes aquellas que todavía no fueron implementadas.

Ejemplos posibles de funcionalidades fuera del alcance actual:

```text
facturación electrónica integrada
reservas online
delivery externo
integración con marketplaces
app móvil nativa
cloud central obligatorio
gestión contable completa
inventario avanzado
recetas y costos complejos
RRHH
fidelización avanzada
```

La eventual incorporación de alguna de estas funciones debe evaluarse según necesidad real.

---

# Alcance de hardware

Marcha no pretende administrar directamente:

```text
routers
switches
impresoras fiscales específicas
hardware propietario
```

salvo futuras integraciones explícitas.

---

# Alcance de Internet

Internet no es requisito para el funcionamiento operativo básico.

Sí puede ser necesario para:

- actualizaciones;
- envío de correo;
- descarga de dependencias durante instalación;
- integraciones futuras.

---

# Alcance multi-restaurante

El modelo soporta separación por restaurante mediante:

```text
restaurant_id
```

Esto permite que la arquitectura pueda evolucionar hacia escenarios con múltiples establecimientos.

No implica automáticamente una plataforma cloud multi-sucursal completa.

---

# Alcance comercial

El producto está orientado inicialmente a establecimientos pequeños y medianos.

La prioridad es resolver correctamente el flujo principal antes de incorporar módulos empresariales complejos.

---

# Criterio de inclusión

Una funcionalidad debería incorporarse al alcance cuando:

1. resuelve un problema real;
2. aparece repetidamente en pilotos o clientes;
3. encaja con la arquitectura;
4. puede mantenerse;
5. aporta más valor que complejidad.

---

# Regla final

El alcance de Marcha debe protegerse de dos extremos:

```text
demasiado poco
→ producto insuficiente

demasiado
→ producto difícil de usar y mantener
```

La prioridad es que el flujo principal del restaurante sea sólido antes de expandir funciones periféricas.