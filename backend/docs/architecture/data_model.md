# Data Model

## Objetivo

Este documento describe el modelo de datos conceptual de Marcha.

Su propósito es explicar:

- qué entidades principales existen;
- qué representa cada una;
- cómo se relacionan;
- qué campos estructurales son relevantes;
- qué relaciones deben respetar `restaurant_id`;
- qué información forma parte del historial operativo.

Este documento no reemplaza los Models SQLAlchemy ni las migraciones Alembic.

> Los Models representan la implementación de persistencia.  
> Este documento explica el significado y las relaciones del modelo.

---

## Visión general

Marcha utiliza un modelo de datos relacional basado en PostgreSQL.

La mayoría de las entidades operativas pertenecen a un restaurante mediante:

```text
restaurant_id
```

De forma simplificada:

```text
Restaurant
│
├── User
│
├── Table
│
├── Category
│   └── Product
│       └── ProductionStation
│
├── Order
│   ├── OrderItem
│   │   └── Product
│   └── Payment
│
├── CashRegister
│   └── CashMovement
│
├── DomainEvent
│
└── SystemSettings
```

Algunas relaciones reales son cruzadas.

Por ejemplo:

```text
Product
   ↓
ProductionStation

Payment
   ↓
CashRegister
```

---

# Entidades principales

## Restaurant

`Restaurant` representa un establecimiento gestionado por Marcha.

Es la entidad raíz de aislamiento lógico del sistema.

Campos principales:

```text
id
```

Las entidades operativas pertenecientes al establecimiento utilizan:

```text
restaurant_id
```

Relaciones conceptuales:

```text
Restaurant
├── Users
├── Tables
├── Categories
├── Products
├── ProductionStations
├── Orders
├── Payments
├── CashRegisters
├── DomainEvents
└── SystemSettings
```

### Regla estructural

Toda entidad que pertenezca a un restaurante debe mantenerse correctamente asociada mediante `restaurant_id`.

Esta relación también constituye una frontera de seguridad.

---

## User

`User` representa una cuenta que puede autenticarse en Marcha.

Campos principales:

```text
id
restaurant_id
username
role
```

El rol se representa mediante el enum:

```text
UserRole
```

Valores actuales:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

Relaciones:

```text
User
   └── pertenece a Restaurant
```

También puede estar relacionado con operaciones realizadas sobre caja, como:

```text
opened_by_id
closed_by_id
user_id en movimientos
```

### Responsabilidad

El usuario determina:

- identidad;
- restaurante;
- permisos operativos.

El frontend puede adaptar la interfaz según el rol, pero la autorización definitiva corresponde al backend.

---

## Table

`Table` representa una mesa física o lógica del restaurante.

Campos principales:

```text
id
restaurant_id
number
occupied
```

Además puede contener información utilizada para representar la mesa dentro del plano del restaurante, como posición y atributos visuales.

Relaciones:

```text
Table
   ├── pertenece a Restaurant
   └── puede estar asociada a Orders
```

Una mesa puede tener distintas órdenes a lo largo del tiempo.

Operativamente, el sistema controla cuál es su orden activa.

### Importante

El estado visual de una mesa no debe interpretarse como fuente independiente de verdad sobre una orden.

La relación con las órdenes determina su situación operativa.

---

## Category

`Category` representa una agrupación de productos.

Ejemplos:

```text
Bebidas
Entradas
Platos
Postres
```

Campos principales:

```text
id
restaurant_id
name
```

Relaciones:

```text
Category
   ├── pertenece a Restaurant
   └── contiene Products
```

Una categoría puede contener múltiples productos.

---

## ProductionStation

`ProductionStation` representa un sector responsable de preparar determinados productos.

Ejemplos:

```text
Cocina
Barra
Parrilla
Cafetería
```

Campos principales:

```text
id
restaurant_id
name
active
```

Relaciones:

```text
ProductionStation
   ├── pertenece a Restaurant
   └── puede estar asociada a múltiples Products
```

### Persistencia histórica

Las estaciones no se eliminan físicamente como operación habitual.

Se utilizan estados de activación:

```text
active = true
active = false
```

Esto permite conservar referencias históricas.

---

## Product

`Product` representa un producto que puede incorporarse a una orden.

Campos principales:

```text
id
restaurant_id
category_id
station_id
name
price
active
```

Relaciones:

```text
Product
   ├── pertenece a Restaurant
   ├── pertenece a Category
   ├── puede pertenecer a ProductionStation
   └── puede aparecer en múltiples OrderItems
```

### Precio

El precio actual del producto se encuentra en:

```text
Product.price
```

Sin embargo, una orden no debe depender exclusivamente del precio actual del producto para reconstruir ventas históricas.

Por ese motivo, cada `OrderItem` conserva:

```text
unit_price
```

correspondiente al momento de la operación.

---

## Order

`Order` representa un pedido.

Campos principales:

```text
id
restaurant_id
table_id
status
created_at
closed_at
discount
```

Relaciones:

```text
Order
   ├── pertenece a Restaurant
   ├── puede pertenecer a Table
   ├── contiene múltiples OrderItems
   └── contiene múltiples Payments
```

El estado se representa mediante:

```text
OrderStatus
```

Estados principales:

```text
OPEN
SENT
IN_PROGRESS
READY
CLOSED
CANCELLED
```

El significado exacto de las transiciones se documenta en:

```text
domain_rules.md
```

---

## OrderItem

`OrderItem` representa un producto concreto dentro de una orden.

Campos principales:

```text
id
restaurant_id
order_id
product_id
quantity
unit_price
status
```

Además puede almacenar información propia del item, como observaciones o notas asociadas a ese producto solicitado.

Relaciones:

```text
OrderItem
   ├── pertenece a Restaurant
   ├── pertenece a Order
   └── referencia Product
```

El estado se representa mediante:

```text
OrderItemStatus
```

Estados principales:

```text
PENDING
SENT
IN_PROGRESS
READY
DELIVERED
CANCELLED
```

### Precio histórico

`unit_price` almacena el precio aplicado al momento de agregar el producto.

Esto permite que:

```text
Product.price
```

pueda cambiar posteriormente sin alterar ventas anteriores.

---

## Relación Order → OrderItem

Una orden contiene múltiples items.

```text
Order 1
   │
   ├── OrderItem A
   ├── OrderItem B
   └── OrderItem C
```

Cada item evoluciona independientemente.

Ejemplo:

```text
Order
├── Hamburguesa → READY
├── Refresco    → DELIVERED
└── Postre      → IN_PROGRESS
```

El estado general de la orden puede derivarse o actualizarse en función del estado de sus items y de las reglas del dominio.

---

## Payment

`Payment` representa un pago realizado sobre una orden.

Campos principales:

```text
id
restaurant_id
order_id
amount
method
cash_register_id
created_at
```

Relaciones:

```text
Payment
   ├── pertenece a Restaurant
   ├── pertenece a Order
   └── puede pertenecer a CashRegister
```

El método de pago se representa mediante:

```text
PaymentMethod
```

Valores actuales:

```text
CASH
CARD
TRANSFER
```

Una orden puede recibir múltiples pagos.

Ejemplo:

```text
Order total: 1.500

Payment
├── CASH      500
└── CARD    1.000
```

---

## CashRegister

`CashRegister` representa una sesión de caja.

No representa la caja física como dispositivo, sino un período operativo desde apertura hasta cierre.

Campos principales:

```text
id
restaurant_id

opened_at
opened_by_id

is_open

opening_amount

closed_at
closed_by_id

total_sales

expected_cash
counted_cash
difference

payments_snapshot
```

Relaciones:

```text
CashRegister
   ├── pertenece a Restaurant
   ├── es abierto por User
   ├── puede ser cerrado por User
   ├── contiene Payments
   └── contiene CashMovements
```

### Apertura

Al abrir una caja se registra:

```text
opening_amount
```

### Cierre

Durante el cierre pueden calcularse:

```text
total_sales
expected_cash
counted_cash
difference
```

donde conceptualmente:

```text
difference = counted_cash - expected_cash
```

---

## CashMovement

`CashMovement` representa un ingreso o egreso de efectivo no originado directamente por un pago de una orden.

Campos principales:

```text
id
cash_register_id
user_id
type
amount
reason
created_at
```

Relaciones:

```text
CashMovement
   ├── pertenece a CashRegister
   └── es realizado por User
```

Tipos conceptuales:

```text
cash_in
cash_out
```

Ejemplos:

```text
cash_in
→ ingreso extraordinario de efectivo

cash_out
→ retiro de efectivo o gasto
```

Los movimientos afectan el cálculo del efectivo esperado.

---

## Relación de caja

De forma simplificada:

```text
CashRegister
│
├── opening_amount
│
├── Payments CASH
│
├── CashMovement cash_in
│
├── CashMovement cash_out
│
└── cierre
     ├── expected_cash
     ├── counted_cash
     └── difference
```

El cálculo conceptual es:

```text
expected_cash =
    opening_amount
    + cash_sales
    + cash_in
    - cash_out
```

Las reglas definitivas pertenecen al dominio y se documentan en `domain_rules.md`.

---

## DomainEvent

`DomainEvent` representa un evento generado como consecuencia de una operación de negocio.

Campos principales:

```text
id
restaurant_id
event_type
payload
created_at
```

`payload` contiene información estructurada asociada al evento.

Ejemplos de eventos:

```text
ORDER_UPDATED
ORDER_STATUS_CHANGED
ITEM_STATUS_CHANGED
ITEM_READY
PAYMENT_ADDED
CASH_MOVEMENT_ADDED
CASH_REGISTER_UPDATED
```

Relaciones:

```text
DomainEvent
   └── pertenece a Restaurant
```

Los detalles de distribución y consumo se documentan en:

```text
realtime_events.md
```

---

## SystemSettings

`SystemSettings` representa configuración persistente correspondiente a un restaurante.

Puede almacenar información relacionada con funcionalidades como:

- backups;
- ejecución automática;
- correo electrónico;
- configuración SMTP;
- estado de tareas programadas.

Relación conceptual:

```text
Restaurant
   ↓
SystemSettings
```

Entre los datos utilizados por el sistema pueden existir valores como:

```text
smtp_host
smtp_port
smtp_user
smtp_password
smtp_from

last_automatic_backup_at
next_automatic_backup_at
last_backup_result
```

La contraseña SMTP se almacena cifrada y no debe considerarse texto plano desde el código consumidor del modelo.

---

# Relaciones principales

## Restaurant → User

```text
Restaurant 1 ─────── N User
```

Un restaurante puede tener múltiples usuarios.

Un usuario pertenece a un restaurante.

---

## Restaurant → Table

```text
Restaurant 1 ─────── N Table
```

---

## Restaurant → Category

```text
Restaurant 1 ─────── N Category
```

---

## Category → Product

```text
Category 1 ─────── N Product
```

---

## ProductionStation → Product

```text
ProductionStation 1 ─────── N Product
```

Una estación puede tener múltiples productos asociados.

---

## Restaurant → Order

```text
Restaurant 1 ─────── N Order
```

---

## Table → Order

```text
Table 1 ─────── N Order
```

Una mesa puede tener múltiples órdenes históricas.

---

## Order → OrderItem

```text
Order 1 ─────── N OrderItem
```

---

## Product → OrderItem

```text
Product 1 ─────── N OrderItem
```

---

## Order → Payment

```text
Order 1 ─────── N Payment
```

Una orden puede pagarse mediante uno o múltiples pagos.

---

## CashRegister → Payment

```text
CashRegister 1 ─────── N Payment
```

---

## CashRegister → CashMovement

```text
CashRegister 1 ─────── N CashMovement
```

---

# Vista relacional simplificada

```text
                           Restaurant
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
              ▼                ▼                 ▼
            User             Table            Category
                                                  │
                                                  ▼
                                               Product
                                                  │
                              ┌───────────────────┤
                              │                   │
                              ▼                   ▼
                    ProductionStation         OrderItem
                                                  ▲
                                                  │
                                               Order
                                              /     \
                                             /       \
                                            ▼         ▼
                                      OrderItem     Payment
                                                       │
                                                       ▼
                                                 CashRegister
                                                       │
                                                       ▼
                                                 CashMovement
```

También existen relaciones directas mediante `restaurant_id` que no se muestran en el diagrama para evitar sobrecargarlo.

---

# Multi-tenancy

Una característica estructural importante del modelo es la presencia de:

```text
restaurant_id
```

en las entidades operativas.

No basta con utilizar relaciones indirectas.

Ejemplo:

```text
OrderItem
   ↓
Order
   ↓
Restaurant
```

Aunque técnicamente podría inferirse el restaurante a partir de la orden, mantener `restaurant_id` explícito en determinadas entidades permite:

- filtrar por tenant;
- proteger consultas;
- simplificar eventos;
- facilitar auditoría;
- evitar accesos cruzados.

Las consultas deben respetar siempre esta pertenencia.

---

# IDs

Las entidades utilizan claves primarias numéricas.

La generación de IDs se realiza mediante PostgreSQL y SQLAlchemy.

La evolución exacta de la definición física pertenece a las migraciones Alembic.

Los IDs:

- identifican registros;
- no implican permisos;
- no deben considerarse secretos.

Conocer el ID de un recurso no autoriza a acceder a él.

---

# Enums

Marcha utiliza enums para representar estados y tipos que poseen un conjunto cerrado de valores.

Enums principales:

```text
UserRole
OrderStatus
OrderItemStatus
PaymentMethod
```

El uso de enums evita representar estados críticos mediante strings arbitrarios.

---

## UserRole

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

---

## OrderStatus

```text
OPEN
SENT
IN_PROGRESS
READY
CLOSED
CANCELLED
```

---

## OrderItemStatus

```text
PENDING
SENT
IN_PROGRESS
READY
DELIVERED
CANCELLED
```

---

## PaymentMethod

```text
CASH
CARD
TRANSFER
```

---

# Valores monetarios

Los valores monetarios deben almacenarse utilizando tipos decimales apropiados.

Ejemplos:

```text
Product.price
Order.discount
OrderItem.unit_price
Payment.amount
CashRegister.opening_amount
CashRegister.expected_cash
CashRegister.counted_cash
CashRegister.difference
CashMovement.amount
```

No debe utilizarse aritmética binaria de punto flotante para reglas monetarias críticas.

En backend los cálculos se realizan utilizando `Decimal`.

---

# Valores calculados

Algunos valores utilizados por la API no corresponden necesariamente a columnas físicas.

Ejemplos:

```text
subtotal
total
paid
remaining
average_ticket
cash_sales
```

Estos valores pueden ser calculados por Services y devueltos mediante Schemas.

> La existencia de un campo en una respuesta API no implica que exista como columna en PostgreSQL.

---

# Datos históricos

Marcha debe conservar suficiente información para reconstruir operaciones anteriores.

Por ese motivo existen decisiones como:

```text
OrderItem.unit_price
```

en lugar de depender del precio actual de `Product`.

Asimismo, determinadas entidades utilizan desactivación o cancelación lógica en lugar de eliminación física.

Ejemplos:

```text
ProductionStation → active
Product           → active
OrderItem enviado → CANCELLED
```

Las reglas exactas de cancelación se documentan en `domain_rules.md`.

---

# Eliminación física y lógica

No todas las entidades siguen la misma estrategia de eliminación.

### Ejemplo de eliminación física válida

Un `OrderItem` en estado:

```text
PENDING
```

puede eliminarse físicamente mientras todavía no forme parte del proceso de producción.

### Ejemplo de cancelación lógica

Una vez enviado:

```text
SENT
IN_PROGRESS
READY
```

debe conservarse la información histórica y utilizarse:

```text
CANCELLED
```

cuando la operación esté permitida.

### Configuración histórica

Entidades como:

```text
Product
ProductionStation
```

pueden utilizar:

```text
active
```

en lugar de eliminarse cuando ya poseen referencias históricas.

---

# Integridad referencial

Las relaciones deben mantener consistencia entre entidades.

Ejemplos:

- un `OrderItem` debe pertenecer a una `Order`;
- el producto de un `OrderItem` debe existir;
- un `Payment` debe pertenecer a una `Order`;
- un `CashMovement` debe pertenecer a una `CashRegister`;
- las entidades relacionadas deben pertenecer al mismo `Restaurant`.

La integridad se protege mediante una combinación de:

```text
constraints de base de datos
+
relaciones SQLAlchemy
+
reglas de dominio
```

---

# Base de datos y migraciones

PostgreSQL es la base de datos de producción.

El esquema se versiona mediante Alembic.

La migración inicial constituye la definición reproducible del esquema desde una base de datos vacía.

Toda modificación futura debe realizarse mediante nuevas migraciones.

No se utiliza:

```python
Base.metadata.create_all()
```

para evolucionar el esquema de producción.

---

# Fuente de verdad

La fuente técnica definitiva sobre el esquema físico es:

```text
Models SQLAlchemy
+
migraciones Alembic
```

Este documento representa una vista conceptual.

Cuando exista una discrepancia entre este documento y el esquema actual, debe:

1. verificarse el Model;
2. verificarse la migración correspondiente;
3. corregirse este documento.

---

# Documentación relacionada

Este documento debe leerse junto con:

```text
architecture_overview.md
architecture_decisions.md
domain_rules.md
realtime_events.md
backend_structure.md
```

### `data_model.md`

Responde a:

> ¿Qué entidades existen y cómo se relacionan?

### `domain_rules.md`

Responde a:

> ¿Qué operaciones y transiciones están permitidas?

### `realtime_events.md`

Responde a:

> ¿Cómo se notifican los cambios entre los clientes?

---

# Resumen conceptual

El núcleo operativo de Marcha puede representarse de esta forma:

```text
Restaurant
   │
   ├── configuración
   │
   ├── usuarios
   │
   ├── mesas
   │
   ├── productos
   │
   └── órdenes
         │
         ├── items
         │     │
         │     └── producción
         │
         └── pagos
               │
               └── caja
```

El modelo busca conservar tres propiedades principales:

> aislamiento entre restaurantes;

> consistencia de las operaciones;

> trazabilidad suficiente de la actividad histórica.