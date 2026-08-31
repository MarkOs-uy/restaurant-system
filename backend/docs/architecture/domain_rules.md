# Domain Rules

## Objetivo

Este documento describe las reglas principales de negocio de Marcha.

Su propósito es centralizar las condiciones que determinan:

- qué operaciones están permitidas;
- qué transiciones de estado son válidas;
- qué condiciones deben cumplirse antes de modificar datos;
- cómo se relacionan pedidos, items, pagos y caja;
- qué datos deben conservarse por razones históricas;
- qué acciones están restringidas según el estado de una entidad.

Estas reglas deben cumplirse siempre en el backend.

> El frontend puede anticipar una validación para mejorar la experiencia de usuario, pero no constituye la autoridad final.

---

# Principios generales

Las reglas de negocio se implementan principalmente en Services.

Los Routers no deben decidir si una operación está permitida.

Cuando una regla no puede cumplirse, el Service debe lanzar:

```text
DomainError
+
ErrorCode
```

Ejemplo conceptual:

```python
raise DomainError(
    "La caja no esta abierta",
    ErrorCode.CASH_REGISTER_NOT_OPEN
)
```

---

# Multi-tenancy

Toda operación sobre entidades pertenecientes a un restaurante debe respetar:

```text
restaurant_id
```

No debe aceptarse una entidad únicamente porque su `id` exista.

Ejemplo correcto:

```python
.filter(
    Product.id == product_id,
    Product.restaurant_id == restaurant_id
)
```

Esta regla se aplica a todas las entidades que pertenezcan a un restaurante.

> Conocer el ID de un recurso no otorga acceso al recurso.

---

# Usuarios y roles

Marcha define actualmente los siguientes roles:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

Cada rol accede a funcionalidades relacionadas con su responsabilidad operativa.

Las restricciones visuales del frontend no reemplazan las validaciones del backend.

---

# Orden

## Estados de una orden

Una orden puede encontrarse en:

```text
OPEN
SENT
IN_PROGRESS
READY
CLOSED
CANCELLED
```

Flujo operativo principal:

```text
OPEN
 ↓
SENT
 ↓
IN_PROGRESS
 ↓
READY
 ↓
CLOSED
```

`CANCELLED` representa una orden cancelada.

---

## OPEN

Una orden en estado `OPEN` representa un pedido todavía editable antes de su envío definitivo a producción.

Puede contener items en estado:

```text
PENDING
```

Durante esta etapa pueden realizarse operaciones como:

- agregar productos;
- modificar cantidades;
- eliminar items pendientes;
- agregar o modificar notas cuando corresponda;
- aplicar otras operaciones permitidas por el dominio.

---

## SENT

Una orden pasa a `SENT` cuando al menos parte de su contenido fue enviado al flujo de producción y corresponde ese estado general.

Los items enviados dejan de comportarse como simples elementos editables del pedido.

A partir de este momento deben respetarse las reglas de trazabilidad.

---

## IN_PROGRESS

Representa una orden con producción en curso.

Puede existir cuando uno o más items se encuentran en:

```text
IN_PROGRESS
```

o cuando el conjunto de estados de sus items determina que la orden se encuentra operativamente en preparación.

---

## READY

Representa una orden cuyos items activos han alcanzado el estado requerido para considerarla preparada.

El estado general de la orden depende de las reglas de sus items.

---

## CLOSED

Una orden cerrada representa una operación finalizada.

Una orden `CLOSED` no debe continuar modificándose mediante el flujo operativo normal.

---

## CANCELLED

Una orden `CANCELLED` representa una operación anulada.

La cancelación debe conservar la información necesaria para mantener trazabilidad.

---

# Cálculo del estado de la orden

El estado de una orden no debe mantenerse de forma arbitraria o independiente de sus items.

Cuando una operación modifica el estado de uno o más `OrderItem`, el Service debe recalcular o determinar el estado correspondiente de la orden.

Ejemplo conceptual:

```text
Order
├── Item A → SENT
├── Item B → IN_PROGRESS
└── Item C → READY
```

El estado general debe representar correctamente la situación operativa del conjunto.

---

# Items de orden

## Estados de OrderItem

Un item puede encontrarse en:

```text
PENDING
SENT
IN_PROGRESS
READY
DELIVERED
CANCELLED
```

Flujo principal:

```text
PENDING
   ↓
SENT
   ↓
IN_PROGRESS
   ↓
READY
   ↓
DELIVERED
```

`CANCELLED` representa una cancelación lógica.

---

# PENDING

`PENDING` representa un producto agregado a la orden pero todavía no enviado a producción.

Mientras permanezca en este estado puede:

- modificarse su cantidad;
- eliminarse físicamente;
- modificarse su nota cuando corresponda.

---

# SENT

`SENT` representa un item ya incorporado al flujo de producción.

Una vez alcanzado este estado:

> el item deja de considerarse un registro descartable.

No debe eliminarse físicamente mediante el flujo normal.

---

# IN_PROGRESS

Representa un item cuya preparación fue iniciada.

---

# READY

Representa un item preparado y disponible para entrega.

---

# DELIVERED

Representa un item ya entregado al cliente.

Es un estado final dentro del flujo operativo normal del producto.

Actualmente un item `DELIVERED` no puede cancelarse mediante el flujo normal.

---

# CANCELLED

Representa un item cancelado después de haber formado parte del proceso operativo.

La cancelación lógica permite conservar:

- producto;
- cantidad;
- precio;
- orden;
- estado histórico;
- contexto de la operación.

---

# Eliminación de items

## Eliminación física

Un item puede eliminarse físicamente únicamente cuando se encuentra en:

```text
PENDING
```

Ejemplo:

```text
PENDING
→ DELETE físico
```

Esto es válido porque todavía no fue enviado a producción.

---

## Cancelación lógica

Un item en:

```text
SENT
IN_PROGRESS
READY
```

no debe eliminarse físicamente.

Cuando la operación esté permitida debe pasar a:

```text
CANCELLED
```

Ejemplo:

```text
SENT
→ CANCELLED

IN_PROGRESS
→ CANCELLED

READY
→ CANCELLED
```

---

## Items entregados

Un item:

```text
DELIVERED
```

no puede cancelarse actualmente mediante el flujo normal.

Si en el futuro se requiere devolución, corrección o anulación contable de items entregados, deberá modelarse como una funcionalidad explícita y no mediante borrado del registro original.

---

# Cantidad de un item

La cantidad puede modificarse únicamente mientras el item permanezca en:

```text
PENDING
```

Una vez enviado a producción, no debe modificarse la cantidad del mismo registro.

Si la cantidad solicitada se reduce a cero mientras está `PENDING`, la operación puede tratarse como eliminación del item.

Ejemplo:

```text
quantity <= 0
→ eliminar OrderItem PENDING
```

---

# Notas de items

Las observaciones operativas pertenecen al `OrderItem`.

Ejemplos:

```text
sin cebolla
sin sal
bien cocido
```

No se considera una única nota general de orden como sustituto de las notas por producto.

Esto permite que cada producto mantenga instrucciones específicas.

---

# Agrupación de items

Cuando Marcha decide agrupar productos equivalentes dentro de una orden, las notas forman parte de la identidad operativa del item.

Dos items no deben fusionarse si poseen instrucciones diferentes.

Ejemplo:

```text
Hamburguesa
nota: sin cebolla
```

no debe agruparse automáticamente con:

```text
Hamburguesa
nota: extra cebolla
```

aunque correspondan al mismo producto.

---

# Envío a producción

Una operación de envío a producción debe actuar únicamente sobre items:

```text
PENDING
```

Los items ya enviados no deben volver a enviarse como si fueran nuevos.

Si no existen items pendientes para enviar, la operación debe rechazarse mediante error de dominio.

---

# Estaciones de producción

Los productos pueden pertenecer a una estación de producción.

Ejemplos:

```text
Cocina
Barra
Parrilla
```

Las estaciones activas participan en el flujo operativo.

---

## Reglas de estaciones

- una estación tiene nombre;
- el nombre no puede ser nulo;
- las estaciones pueden activarse o desactivarse;
- las estaciones no se eliminan físicamente como operación habitual;
- cocina consulta estaciones activas;
- los mozos no necesitan consultar estaciones para operar.

---

# Productos

Un producto pertenece a un restaurante.

Puede asociarse a:

```text
Category
ProductionStation
```

El producto posee un precio actual:

```text
Product.price
```

Los productos pueden activarse o desactivarse.

---

# Precio histórico de un item

Cuando un producto se agrega a una orden, el item debe almacenar:

```text
unit_price
```

Este valor representa el precio aplicado en esa operación.

Los cálculos históricos no deben depender del valor actual de:

```text
Product.price
```

Ejemplo:

```text
Hoy:
Product.price = 500

OrderItem.unit_price = 500

Mañana:
Product.price = 550
```

La orden anterior debe continuar utilizando:

```text
500
```

---

# Totales de una orden

Los totales deben calcularse en backend utilizando valores monetarios decimales.

Conceptualmente:

```text
subtotal =
sum(
    quantity × unit_price
    de items activos
)
```

Los items cancelados no deben formar parte del total cobrable.

---

# Descuentos

Una orden puede contener descuento.

Regla principal:

```text
discount <= subtotal
```

El descuento no puede producir un total negativo.

Conceptualmente:

```text
total = subtotal - discount
```

con:

```text
total >= 0
```

---

# Pagos

Una orden puede recibir múltiples pagos.

Métodos actuales:

```text
CASH
CARD
TRANSFER
```

Cada pago contiene:

```text
amount
method
order_id
cash_register_id
```

---

# Saldo de una orden

Conceptualmente:

```text
paid =
sum(payments)

remaining =
total - paid
```

El backend debe calcular los valores monetarios mediante `Decimal`.

---

# Pago superior al saldo

No debe registrarse un pago que viole la regla vigente de saldo pendiente.

Si un pago supera el importe permitido, debe rechazarse mediante error de dominio.

Ejemplo de código de error:

```text
PAYMENT_EXCEEDS_REMAINING
```

---

# Caja abierta requerida

Las operaciones que forman parte del flujo de caja deben validar que exista una caja abierta cuando corresponda.

Si no existe:

```text
CASH_REGISTER_NOT_OPEN
```

La existencia de una caja abierta debe verificarse en backend.

---

# Cash Register

Una sesión de caja representa el período entre apertura y cierre.

Solo debe existir una caja abierta válida por restaurante según las reglas actuales del sistema.

---

# Apertura de caja

Una caja se abre indicando:

```text
opening_amount
```

Si ya existe una caja abierta, debe rechazarse una nueva apertura.

Error conceptual:

```text
CASH_REGISTER_ALREADY_OPEN
```

---

# Movimientos de caja

Marcha permite movimientos de:

```text
cash_in
cash_out
```

Cada movimiento contiene:

```text
amount
reason
user_id
cash_register_id
```

Solo pueden registrarse cuando existe una caja abierta.

---

# Efectivo esperado

El efectivo esperado se calcula conceptualmente como:

```text
expected_cash =
    opening_amount
    + cash_sales
    + cash_in
    - cash_out
```

Solo los pagos realizados mediante:

```text
CASH
```

afectan directamente el efectivo esperado por ventas.

---

# Cierre de caja

Para cerrar una caja deben cumplirse las condiciones definidas por el dominio.

Actualmente no debe permitirse cerrar la caja si existen órdenes abiertas pendientes.

Error conceptual:

```text
CASH_REGISTER_PENDING_ORDERS
```

Durante el cierre se registra:

```text
counted_cash
```

y se calcula:

```text
difference =
counted_cash - expected_cash
```

También puede conservarse un snapshot de los pagos por método.

---

# Cierre de una orden

Una orden no puede cerrarse únicamente porque el usuario solicite la operación.

Deben cumplirse las reglas siguientes.

---

## Saldo

La orden debe tener:

```text
remaining == 0
```

Si existe saldo pendiente:

```text
ORDER_HAS_REMAINING_BALANCE
```

---

## Items entregados

Todos los items activos que requieren entrega deben encontrarse en el estado correspondiente.

Actualmente:

```text
DELIVERED
```

Los items cancelados no deben impedir el cierre.

Si existen items activos no entregados:

```text
ORDER_ITEMS_NOT_DELIVERED
```

---

## Orden cerrada

Una orden ya cerrada no puede volver a cerrarse ni modificarse mediante el flujo operativo habitual.

Error conceptual:

```text
ORDER_ALREADY_CLOSED
```

---

# Cancelación de una orden

Una orden puede cancelarse mientras su estado y su situación operativa lo permitan.

Una orden:

```text
CLOSED
```

no debe cancelarse mediante el flujo normal.

La cancelación debe mantener la trazabilidad de la operación.

---

# Orden sin items activos

Cuando una operación de cancelación o eliminación deja a una orden sin items activos, el sistema debe recalcular su estado.

Cuando corresponda, la orden puede pasar a:

```text
CANCELLED
```

en lugar de permanecer artificialmente abierta sin contenido operativo.

---

# Transiciones de estado

Las transiciones deben validarse explícitamente.

No debe aceptarse cualquier cambio simplemente porque el cliente envíe un nuevo valor.

Ejemplo:

```text
PENDING → READY
```

no debe permitirse si la transición válida requiere pasar por estados intermedios.

Las transiciones inválidas deben producir:

```text
INVALID_TRANSITION
```

o el código específico correspondiente.

---

# Permisos sobre estados

No todos los roles pueden modificar cualquier estado.

Ejemplo conceptual:

```text
WAITER
→ acciones de salón y entrega

KITCHEN
→ acciones de producción

CASHIER
→ pagos y caja

ADMIN
→ capacidades administrativas ampliadas
```

Cuando un rol intenta realizar una transición no autorizada debe rechazarse.

Ejemplo:

```text
ITEM_STATUS_ROLE_FORBIDDEN
```

---

# Eventos de dominio

Las operaciones relevantes pueden emitir eventos después de realizar el cambio de negocio correspondiente.

Ejemplo:

```text
cambio de estado
   ↓
persistencia
   ↓
commit
   ↓
evento
```

Los eventos no sustituyen las reglas de dominio.

El detalle de eventos se documenta en:

```text
realtime_events.md
```

---

# Commit y consistencia

Una operación de negocio puede modificar múltiples entidades.

Ejemplo:

```text
agregar pago
   ↓
Payment
Order
CashRegister
DomainEvent
```

El Service debe asegurar que la operación se mantenga coherente.

El Router no determina los límites de transacción.

---

# Backups

Los backups forman parte de la operación administrativa del sistema.

Marcha soporta:

- backups manuales;
- automáticos;
- diarios;
- semanales;
- mensuales;
- backups previos a restauración.

Las reglas exactas de scheduling pertenecen al módulo de backup.

---

# Restauración

Antes de determinadas restauraciones se debe preservar un backup previo cuando corresponda.

Una restauración no debe ejecutarse de forma que destruya silenciosamente el estado actual sin mecanismo de recuperación.

---

# SMTP

Las funciones de correo requieren configuración SMTP válida.

Si la funcionalidad requiere SMTP y no se encuentra configurado, debe rechazarse mediante error de dominio.

Ejemplo:

```text
SMTP_NOT_CONFIGURED
```

La falta de SMTP no debe impedir las operaciones principales del restaurante.

---

# Datos sensibles

Las credenciales sensibles no deben exponerse como texto plano al frontend.

La contraseña SMTP se almacena cifrada.

La clave utilizada para descifrarla no forma parte de la base de datos.

---

# Licenciamiento

En producción, Marcha requiere una licencia válida antes de iniciar el backend.

La licencia debe:

- existir;
- ser válida;
- tener una firma criptográfica correcta;
- corresponder a la máquina autorizada;
- no estar vencida cuando exista fecha de expiración.

Si la licencia no cumple estas condiciones:

> el backend no debe iniciar.

---

# Estado del sistema frente a fallo de licencia

La existencia de contenedores activos no significa que Marcha esté operativo.

El sistema se considera disponible únicamente cuando el backend supera la validación de licencia y responde correctamente.

---

# Reglas de historial

Las operaciones históricas importantes no deben perderse por simplificar la interfaz.

Ejemplos:

- un precio anterior debe conservarse en `OrderItem.unit_price`;
- una estación utilizada históricamente no debería desaparecer físicamente;
- un item enviado a producción no debería eliminarse físicamente;
- una cancelación debe preservar la evidencia de que el item existió.

---

# Borrado lógico vs físico

La estrategia depende del estado y del valor histórico de la entidad.

## Borrado físico permitido

Ejemplo:

```text
OrderItem PENDING
```

si todavía no fue enviado.

## Borrado lógico / desactivación

Ejemplos:

```text
OrderItem enviado → CANCELLED

Product → active = false

ProductionStation → active = false
```

---

# Reglas monetarias

Todas las reglas monetarias críticas deben ejecutarse en backend utilizando:

```text
Decimal
```

No debe utilizarse `float` como autoridad para:

- totales;
- pagos;
- descuentos;
- saldo;
- caja;
- diferencias.

---

# Validación frontend

El frontend puede impedir visualmente acciones inválidas.

Ejemplo:

```text
deshabilitar botón Cerrar Orden
```

si existe saldo pendiente.

Pero el backend debe repetir siempre la validación.

> Una regla visible en el frontend sin validación backend no se considera una regla implementada.

---

# Errores de dominio

Los códigos de error deben representar condiciones estables.

Ejemplos actuales:

```text
ORDER_NOT_FOUND
ORDER_ALREADY_CLOSED
ORDER_ITEMS_NOT_DELIVERED
ORDER_EMPTY
ORDER_HAS_REMAINING_BALANCE
INVALID_TRANSITION

ITEM_NOT_FOUND
ITEM_NOT_IN_ORDER
ITEM_ALREADY_SENT
NOT_PENDING_ITEMS_TO_SEND
ITEM_STATUS_ROLE_FORBIDDEN
ITEM_INVALID_TRANSITION

TABLE_NOT_FOUND

PAYMENT_NOT_FOUND
PAYMENT_INVALID_METHOD
PAYMENT_EXCEEDS_REMAINING

CASH_REGISTER_NOT_OPEN
CASH_REGISTER_ALREADY_OPEN
CASH_REGISTER_PENDING_ORDERS

CATEGORY_EXISTS
STATION_NAME_ALREADY_EXISTS
```

El texto del mensaje puede evolucionar.

El código debe mantenerse estable siempre que represente la misma condición.

---

# Fuente de verdad

La fuente definitiva de una regla concreta es el código de dominio vigente.

Principalmente:

```text
domain/*/*_service.py
```

Este documento representa una descripción consolidada de dichas reglas.

Si existe una discrepancia entre este documento y el código:

1. revisar el Service;
2. revisar la decisión arquitectónica correspondiente;
3. determinar cuál es el comportamiento correcto;
4. actualizar código o documentación según corresponda.

---

# Documentación relacionada

Este documento se complementa con:

```text
data_model.md
realtime_events.md
architecture_decisions.md
backend_structure.md
backend_standards.md
```

### `data_model.md`

Responde a:

> ¿Qué entidades existen?

### `domain_rules.md`

Responde a:

> ¿Qué puede hacerse con esas entidades?

### `realtime_events.md`

Responde a:

> ¿Cómo se comunican los cambios a otros clientes?

---

# Principio final

Las reglas del dominio deben representar el comportamiento real del restaurante, no únicamente las necesidades de una pantalla.

Cuando exista una duda sobre dónde implementar una condición, debe preguntarse:

> ¿Esta regla debe seguir siendo cierta aunque la operación se invoque desde otro endpoint, otro cliente o una futura interfaz?

Si la respuesta es sí, la regla pertenece al dominio.