# Realtime Events

## Objetivo

Este documento describe el sistema de eventos en tiempo real utilizado por Marcha.

Su propósito es explicar:

- qué tipos de eventos existen;
- cuándo se emiten;
- quién los consume;
- cómo se distribuyen;
- qué responsabilidad tienen Redis y WebSockets;
- cómo debe reaccionar el frontend;
- qué principios deben respetarse al agregar eventos nuevos.

Este documento no reemplaza la implementación concreta del sistema de eventos.

> Los eventos notifican cambios.  
> El estado definitivo sigue perteneciendo al backend y a la base de datos.

---

# Visión general

Marcha utiliza eventos en tiempo real para mantener sincronizados los distintos clientes conectados dentro del restaurante.

Ejemplos de clientes:

```text
Waiter
Kitchen
Cashier
Admin
```

Cuando una operación de negocio modifica información relevante, el backend puede emitir un evento.

Ejemplo:

```text
Mozo envía pedido
        ↓
OrderService
        ↓
modifica Order / OrderItem
        ↓
commit
        ↓
emite evento
        ↓
Redis
        ↓
WebSocket
        ↓
Kitchen
```

---

# Principio fundamental

Los eventos deben representar operaciones de negocio que realmente ocurrieron.

Por ese motivo:

> Los eventos se emiten desde los Services, nunca desde los Routers.

Esto evita situaciones como:

```text
Router recibe request
→ emite evento
→ operación de negocio falla
```

El evento debe producirse después de que el cambio correspondiente haya sido validado y persistido correctamente.

---

# Arquitectura general

El flujo conceptual es:

```text
Cliente A
   ↓
HTTP
   ↓
Router
   ↓
Service
   ↓
PostgreSQL
   ↓
Domain Event
   ↓
Redis
   ↓
WebSocket Manager
   ↓
Cliente B / C / D
```

---

# Redis

Redis actúa como mecanismo de distribución de eventos entre componentes del backend.

Su función principal es facilitar:

- publicación;
- distribución;
- desacoplamiento;
- sincronización entre procesos.

Redis no constituye la fuente definitiva del estado del negocio.

La fuente de verdad continúa siendo:

```text
PostgreSQL
```

---

# WebSockets

Los WebSockets permiten enviar eventos a los clientes conectados sin esperar una nueva solicitud HTTP.

En producción el flujo es:

```text
Browser
   ↓
/ws
   ↓
Nginx
   ↓
FastAPI WebSocket
```

El frontend no debe depender de un hostname fijo.

Debe poder funcionar tanto mediante:

```text
http://pos.local
```

como mediante:

```text
http://<IP-local>
```

---

# Filosofía de sincronización

Marcha utiliza el siguiente principio:

> WebSocket notifica. HTTP confirma.

Esto significa que un evento puede indicar:

```text
ORDER_UPDATED
```

sin necesidad de contener toda la representación completa de la orden.

El cliente puede reaccionar haciendo:

```text
evento
   ↓
loadOrder()
   ↓
GET /orders/{id}
   ↓
estado actualizado
```

Este patrón reduce inconsistencias y evita duplicar la lógica de reconstrucción del estado en múltiples clientes.

---

# Eventos persistidos

Marcha puede registrar eventos mediante la entidad:

```text
DomainEvent
```

Campos principales:

```text
id
restaurant_id
event_type
payload
created_at
```

El evento persistido permite conservar información relacionada con acciones relevantes del dominio.

La persistencia y la distribución en tiempo real son responsabilidades relacionadas, pero no equivalentes.

---

# Estructura conceptual de un evento

Un evento contiene al menos información suficiente para identificar:

```text
restaurant_id
event_type
payload
```

Además, según el mecanismo de distribución, puede incluir:

```text
target
target_id
```

Ejemplo conceptual:

```json
{
  "restaurant_id": 1,
  "event_type": "ITEM_READY",
  "payload": {
    "order_id": 25,
    "item_id": 89
  },
  "target": "role",
  "target_id": "WAITER"
}
```

El payload debe mantenerse lo más pequeño posible.

---

# Tipos de destino

Los eventos pueden distribuirse según distintos criterios.

Los principales son:

```text
role
station
broadcast
```

---

## Distribución por rol

Permite notificar a todos los clientes conectados con un determinado rol.

Ejemplo:

```text
target = role
target_id = CASHIER
```

Puede utilizarse para eventos como:

```text
PAYMENT_ADDED
CASH_REGISTER_UPDATED
ORDER_CLOSED
```

---

## Distribución por estación

Permite enviar información únicamente a clientes asociados a una estación de producción.

Ejemplo:

```text
target = station
target_id = 3
```

Esto permite que:

```text
Barra
```

no reciba necesariamente eventos destinados exclusivamente a:

```text
Cocina
```

---

## Broadcast

Algunos eventos pueden ser relevantes para todos los clientes conectados al restaurante.

En esos casos puede utilizarse distribución general.

Debe evitarse utilizar broadcast cuando existe un destinatario más específico.

> Los eventos deben enviarse únicamente a quienes realmente necesitan reaccionar.

---

# Eventos principales

Los eventos pueden evolucionar con el sistema.

A continuación se documentan los principales eventos utilizados actualmente.

---

# ORDER_UPDATED

Indica que una orden fue modificada.

Ejemplos de causas:

- agregado de item;
- eliminación de item pendiente;
- modificación de cantidad;
- cancelación;
- actualización relacionada con sus items.

Payload mínimo recomendado:

```json
{
  "order_id": 25
}
```

Consumidores habituales:

```text
WAITER
CASHIER
ADMIN
```

El cliente puede reaccionar recargando:

```text
GET /orders/{order_id}
```

---

# ORDER_STATUS_CHANGED

Indica que cambió el estado general de una orden.

Ejemplo:

```text
SENT → IN_PROGRESS
```

Payload conceptual:

```json
{
  "order_id": 25,
  "status": "IN_PROGRESS"
}
```

Consumidores posibles:

```text
WAITER
KITCHEN
CASHIER
ADMIN
```

La respuesta concreta depende de la pantalla.

---

# ORDER_CLOSED

Indica que una orden fue cerrada.

Payload habitual:

```json
{
  "order_id": 25
}
```

Consumidores habituales:

```text
ADMIN
WAITER
CASHIER
```

El evento puede utilizarse para:

- retirar la orden de listas activas;
- refrescar mesas;
- refrescar caja;
- actualizar reportes cuando corresponda.

---

# ITEM_STATUS_CHANGED

Indica que cambió el estado de un `OrderItem`.

Ejemplo:

```text
SENT → IN_PROGRESS
```

o:

```text
READY → DELIVERED
```

Payload conceptual:

```json
{
  "order_id": 25,
  "item_id": 89,
  "status": "READY"
}
```

Consumidores posibles:

```text
WAITER
KITCHEN
CASHIER
ADMIN
```

El destinatario depende de la transición y del contexto.

---

# ITEM_READY

Indica específicamente que un item alcanzó:

```text
READY
```

Este evento existe porque el paso a `READY` suele requerir una reacción operativa inmediata por parte del salón.

Ejemplo:

```text
Cocina termina producto
   ↓
ITEM_READY
   ↓
Waiter
   ↓
notificación visual / sonora
```

Payload conceptual:

```json
{
  "order_id": 25,
  "item_id": 89
}
```

El cliente Waiter puede:

- reproducir sonido;
- destacar la orden;
- refrescar datos.

---

# PAYMENT_ADDED

Indica que se registró un pago sobre una orden.

Payload conceptual:

```json
{
  "order_id": 25,
  "payment_id": 42
}
```

Consumidores habituales:

```text
CASHIER
ADMIN
WAITER
```

Puede provocar:

- actualización del saldo;
- actualización de caja;
- cambio de acciones disponibles;
- refresco de la orden.

---

# CASH_MOVEMENT_ADDED

Indica que se registró un movimiento manual de caja.

Ejemplo:

```text
cash_in
cash_out
```

Payload conceptual:

```json
{
  "cash_register_id": 12,
  "movement_id": 8
}
```

Consumidores habituales:

```text
CASHIER
ADMIN
```

---

# CASH_REGISTER_UPDATED

Indica que cambió información relevante de la caja.

Ejemplos:

- nuevo pago;
- nuevo movimiento;
- apertura;
- actualización de totales;
- cierre cuando corresponda.

Payload mínimo conceptual:

```json
{
  "cash_register_id": 12
}
```

o, cuando la actualización deriva de una orden:

```json
{
  "order_id": 25
}
```

El consumidor habitual es:

```text
CASHIER
```

---

# Eventos y estaciones de producción

Los eventos relacionados con producción deben respetar la estación asociada al producto.

Ejemplo:

```text
Order
├── Hamburguesa → Cocina
└── Refresco    → Barra
```

Cuando se envían ambos items:

```text
Cocina recibe solamente Hamburguesa
Barra recibe solamente Refresco
```

No debe dependerse del frontend para filtrar información que el backend puede dirigir correctamente.

---

# Emisión de eventos

La emisión debe realizarse desde la operación de dominio que produce el cambio.

Ejemplo conceptual:

```python
self.db.commit()

self.events.emit(
    restaurant_id=restaurant_id,
    event_type="ORDER_UPDATED",
    payload={
        "order_id": order.id
    },
    target="role",
    target_id=UserRole.WAITER.value
)
```

La implementación concreta puede variar, pero debe mantenerse el principio:

```text
validar
   ↓
modificar
   ↓
persistir
   ↓
emitir
```

---

# Commit antes del evento

Como regla general, el cliente no debe ser notificado de un cambio que todavía no fue persistido correctamente.

Por ello:

> El evento debe representar un estado que el cliente pueda consultar inmediatamente mediante HTTP.

Ejemplo incorrecto:

```text
emitir ORDER_UPDATED
   ↓
commit falla
```

El cliente recibiría una notificación sobre un estado inexistente.

---

# Payloads

Los payloads deben mantenerse pequeños y orientados a identificación.

Preferible:

```json
{
  "order_id": 25
}
```

en lugar de enviar toda la orden completa si el cliente puede consultarla mediante API.

Ventajas:

- menor acoplamiento;
- eventos más estables;
- payloads pequeños;
- menos duplicación de Schemas;
- menor riesgo de estado parcial.

---

# Información suficiente

Un payload debe contener suficiente información para que el receptor determine:

- qué cambió;
- qué recurso consultar;
- si el evento le afecta.

No debe contener información adicional únicamente porque esté disponible en el Service.

---

# Eventos y seguridad

Los eventos deben respetar siempre:

```text
restaurant_id
```

Un cliente conectado a un restaurante no debe recibir información perteneciente a otro.

La distribución en tiempo real forma parte de la frontera de aislamiento multi-tenant.

---

# Autorización

La recepción de un evento no otorga permisos adicionales.

El frontend puede recibir una referencia a un recurso, pero cualquier consulta HTTP posterior debe volver a ser autorizada por el backend.

---

# Comportamiento del frontend

Cada Page debe escuchar únicamente eventos relevantes.

Ejemplo:

```text
KitchenPage
→ eventos de producción

CashierPage
→ pagos y caja

Waiter
→ órdenes e items preparados
```

Debe evitarse registrar manejadores generales que recarguen toda la aplicación ante cualquier evento.

---

# Cliente que originó la operación

El cliente que ejecutó una operación HTTP no debe depender exclusivamente de recibir su propio WebSocket para actualizarse.

Ejemplo preferido:

```typescript
await apiFetch(...)

await loadOrder()
```

Mientras tanto:

```text
WebSocket
```

sincroniza otros dispositivos.

Esto evita depender de:

- latencia del WebSocket;
- orden de llegada;
- reconexiones;
- pérdida temporal de eventos.

---

# Sonido de notificación

Algunos eventos pueden generar una señal sonora.

Ejemplo:

```text
ITEM_READY
```

puede provocar:

```typescript
playSound()
```

en la interfaz de Waiter.

El sonido forma parte de la experiencia de usuario.

No constituye una regla de negocio.

Si el navegador bloquea la reproducción automática, la operación del sistema debe continuar normalmente.

---

# Reconexión

Una conexión WebSocket puede interrumpirse temporalmente por:

- pérdida de Wi-Fi;
- suspensión del dispositivo;
- reinicio del backend;
- cambio de red;
- cierre temporal del navegador.

El frontend debe asumir que una conexión puede perderse.

Después de una reconexión, debe obtener nuevamente mediante HTTP cualquier estado crítico que necesite mostrar.

> Los eventos no constituyen un historial completo que el navegador pueda asumir que recibió íntegramente.

---

# Pérdida de eventos

Marcha debe continuar siendo consistente aunque un cliente pierda uno o más eventos.

Ejemplo:

```text
ITEM_READY
```

puede no llegar por una interrupción de red.

Al volver a consultar:

```text
GET /orders/active
```

el cliente debe poder descubrir que el item ya se encuentra en `READY`.

Por este motivo la base de datos es la fuente definitiva del estado.

---

# Idempotencia del frontend

La recepción repetida de un evento no debería provocar corrupción del estado.

Ejemplo:

```text
ORDER_UPDATED
ORDER_UPDATED
```

puede simplemente producir:

```text
loadOrder()
```

dos veces.

El comportamiento debe ser seguro aunque existan eventos duplicados.

---

# Orden de eventos

Los clientes no deberían asumir que distintos eventos siempre llegarán exactamente en el orden esperado.

Ejemplo:

```text
ITEM_STATUS_CHANGED
ORDER_STATUS_CHANGED
```

pueden producir actualizaciones muy próximas entre sí.

Cuando el orden sea crítico, el frontend debe consultar nuevamente el estado actual mediante HTTP.

---

# WebSocket vs estado de dominio

El estado de una entidad no se encuentra almacenado en el WebSocket.

Ejemplo:

```text
Order.status
```

vive en PostgreSQL.

WebSocket únicamente comunica:

```text
algo cambió
```

Esta separación permite que:

- el frontend se reconecte;
- nuevos clientes obtengan estado actual;
- el sistema sobreviva a eventos perdidos.

---

# Errores en eventos

Un fallo al enviar una notificación en tiempo real no debe transformar una operación de negocio ya confirmada en una operación inexistente.

Ejemplo:

```text
Payment creado correctamente
   ↓
commit OK
   ↓
fallo WebSocket
```

El pago continúa siendo válido.

Los clientes podrán recuperar el nuevo estado mediante HTTP.

La política concreta de logging o reintento puede evolucionar sin modificar esta regla conceptual.

---

# Nuevos eventos

Antes de crear un nuevo `event_type`, debe verificarse que no exista un evento actual que pueda representar correctamente el mismo cambio.

Un evento nuevo debe justificar una necesidad concreta.

Preguntas recomendadas:

1. ¿Qué operación de negocio representa?
2. ¿Qué cliente necesita conocerla?
3. ¿Por qué un evento existente no es suficiente?
4. ¿Qué payload mínimo necesita?
5. ¿Debe distribuirse por rol, estación o broadcast?
6. ¿Puede el cliente recuperar el estado mediante HTTP?
7. ¿Qué ocurre si el evento se pierde?

---

# Nomenclatura

Los tipos de evento utilizan nombres en mayúsculas con `_`.

Ejemplo:

```text
ORDER_UPDATED
ITEM_STATUS_CHANGED
ITEM_READY
PAYMENT_ADDED
```

Debe utilizarse una nomenclatura que represente un hecho ocurrido.

Preferible:

```text
PAYMENT_ADDED
```

frente a:

```text
ADD_PAYMENT
```

porque el evento representa algo que ya sucedió.

---

# Estabilidad de eventos

Los nombres de eventos forman parte del contrato entre backend y frontend.

Cambiar:

```text
ITEM_READY
```

por otro nombre puede romper clientes existentes.

Los eventos deben modificarse con el mismo cuidado que un endpoint API.

---

# Cambios de payload

Agregar campos opcionales suele ser menos riesgoso que eliminar o renombrar campos utilizados por clientes.

Cuando sea necesario un cambio incompatible, debe revisarse:

- backend;
- types del frontend;
- reducers o handlers;
- Pages consumidoras.

---

# Tipado frontend

Los eventos deben representarse mediante tipos TypeScript compartidos.

Ejemplo conceptual:

```typescript
type WebSocketEvent = {
  event_type: WebSocketEventType
  payload: Record<string, unknown>
}
```

Cuando un evento posee una estructura estable y relevante, puede utilizarse un tipo más específico.

Los nombres y casing deben coincidir exactamente con los valores enviados por backend.

---

# Observabilidad

Los errores relacionados con WebSockets o eventos deben registrarse cuando ayuden al diagnóstico.

Debe ser posible diferenciar al menos conceptualmente:

```text
fallo de conexión
fallo de distribución
evento inválido
cliente desconectado
```

Los logs no deben exponer secretos ni información sensible innecesaria.

---

# Eventos actuales resumidos

| Evento | Significado | Consumidores habituales |
|---|---|---|
| `ORDER_UPDATED` | La orden cambió | Waiter, Cashier, Admin |
| `ORDER_STATUS_CHANGED` | Cambió el estado de la orden | Waiter, Kitchen, Cashier, Admin |
| `ORDER_CLOSED` | La orden fue cerrada | Waiter, Cashier, Admin |
| `ITEM_STATUS_CHANGED` | Cambió el estado de un item | Waiter, Kitchen, Cashier, Admin |
| `ITEM_READY` | Un item quedó listo para entregar | Waiter |
| `PAYMENT_ADDED` | Se registró un pago | Cashier, Admin, Waiter |
| `CASH_MOVEMENT_ADDED` | Se registró un ingreso o egreso de caja | Cashier, Admin |
| `CASH_REGISTER_UPDATED` | Cambió el estado o resumen de caja | Cashier, Admin |

La audiencia exacta puede variar según la operación que origina el evento.

La implementación del backend constituye la fuente definitiva para verificar los destinatarios concretos.

---

# Fuente de verdad

La fuente técnica definitiva sobre eventos es la implementación vigente del backend y frontend.

Principalmente:

```text
Services del dominio
Event Service / Event Bus
WebSocket Manager
handlers WebSocket frontend
types/webSocketEvents.ts
```

Este documento describe el comportamiento conceptual.

Si existe una discrepancia:

1. revisar el Service que emite el evento;
2. revisar la implementación de distribución;
3. revisar los consumidores frontend;
4. determinar el comportamiento correcto;
5. actualizar código o documentación.

---

# Documentación relacionada

Este documento debe leerse junto con:

```text
architecture_overview.md
architecture_decisions.md
data_model.md
domain_rules.md
backend_structure.md
frontend_structure.md
```

### `data_model.md`

Responde a:

> ¿Qué entidades cambian?

### `domain_rules.md`

Responde a:

> ¿Qué cambios están permitidos?

### `realtime_events.md`

Responde a:

> ¿Cómo se enteran los demás clientes de esos cambios?

---

# Principio final

El sistema de eventos de Marcha debe permitir sincronización rápida sin convertir al WebSocket en una segunda base de datos.

La regla fundamental es:

```text
PostgreSQL
   ↓
estado real

HTTP
   ↓
consulta del estado real

WebSocket
   ↓
notificación de que algo cambió
```

Si un cliente puede perder todos los eventos durante algunos segundos, reconectarse y reconstruir correctamente su pantalla mediante HTTP, la arquitectura de tiempo real está cumpliendo su objetivo.