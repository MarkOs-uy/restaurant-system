# Testing Strategy

## Objetivo

Este documento define la estrategia de testing de Marcha.

El objetivo no es alcanzar una cantidad arbitraria de tests o un porcentaje de cobertura por sí mismo.

El objetivo es proteger:

- dinero;
- estado de órdenes;
- caja;
- aislamiento entre restaurantes;
- permisos;
- persistencia;
- backups;
- migraciones;
- funcionamiento operativo completo.

> Se priorizan las consecuencias de un error, no la cantidad de líneas cubiertas.

---

# Principio general

Marcha es un sistema operativo para restaurantes.

Un error puede producir:

```text
cobros incorrectos
órdenes inconsistentes
productos perdidos
caja incorrecta
acceso a datos de otro restaurante
pérdida de backups
interrupción del servicio
```

Por ello, el testing se prioriza por riesgo.

---

# Prioridades

Se utilizan niveles conceptuales:

```text
P0
P1
P2
```

---

## P0 — crítico

Una regresión P0 puede afectar directamente:

- dinero;
- caja;
- órdenes;
- pagos;
- estados operativos;
- integridad fundamental.

Debe contar con tests automatizados siempre que sea razonablemente posible.

Ejemplos:

```text
CashRegisterService
OrderService
Payment rules
OrderItem transitions
Order closing
```

---

## P1 — alto

Protege funcionalidades críticas de seguridad o recuperación.

Ejemplos:

```text
authentication
permissions
multi-tenancy
backup
restore
licensing
```

---

## P2 — medio

Funcionalidades importantes pero con menor impacto inmediato.

Ejemplos:

```text
administración
productos
categorías
estaciones
layout
reportes secundarios
UX
```

Esto no significa que P2 no deba probarse.

Significa que, ante tiempo limitado, P0 y P1 tienen prioridad.

---

# Pirámide de testing

La estrategia combina:

```text
           E2E / Pilot
              ▲
        Integration Tests
              ▲
          Unit Tests
```

Se busca tener:

- muchos tests rápidos de dominio;
- menos tests de integración;
- pocos tests end-to-end bien elegidos;
- validación real durante pilotos.

---

# Unit Tests

Los tests unitarios actuales se encuentran en:

```text
backend/tests/unit/
```

Actualmente cubren áreas como:

```text
OrderService
CashRegisterService
Authentication / Permissions
BackupService
```

La suite seguirá creciendo por riesgo funcional.

---

# Fixtures comunes

Se utilizan fixtures de pytest en:

```text
tests/conftest.py
```

Fixtures actuales:

```text
db
restaurant
user
table
product
order
```

Cada test obtiene datos aislados.

---

# Base de datos unitaria

Los tests unitarios actuales utilizan:

```text
SQLite in-memory
```

mediante:

```python
create_engine("sqlite:///:memory:")
```

y:

```python
Base.metadata.create_all(engine)
```

Esta excepción es intencional.

En producción, Alembic es la autoridad del esquema.

En estos tests:

```text
create_all()
```

se utiliza únicamente para construir rápidamente una base efímera y aislada.

---

# Ventajas de SQLite in-memory

Permite tests:

- rápidos;
- independientes;
- sin PostgreSQL activo;
- sin tocar datos reales;
- reproducibles.

Cada test descarta su base al finalizar.

---

# Limitación de SQLite

SQLite no reproduce exactamente todo el comportamiento de PostgreSQL.

Diferencias posibles:

```text
native enums
constraints
locking
SQL dialect
transaction semantics
JSON behavior
concurrency
```

Por ello:

> Los unit tests con SQLite no sustituyen los tests de integración con PostgreSQL.

---

# Factories

Las funciones auxiliares se mantienen en:

```text
tests/unit/factories.py
```

Ejemplos:

```text
crear_pago()
crear_movimiento_caja()
crear_orden()
crear_item()
```

Las factories:

- reducen repetición;
- facilitan preparar escenarios;
- no deben ocultar reglas de negocio.

Cuando se desea probar el flujo real, debe utilizarse el Service en lugar de construir directamente el estado final mediante factory.

---

# P0 — Cash Register

Los tests de caja protegen especialmente:

```text
apertura
cierre
expected_cash
diferencia
movimientos
ventas
```

---

## Apertura negativa

Debe rechazarse:

```text
opening_amount < 0
```

---

## Segunda caja abierta

No debe permitirse abrir una nueva caja si ya existe una abierta para el restaurante.

---

## Efectivo esperado

Debe comprobarse:

```text
expected_cash =
opening_amount
+ cash_sales
+ cash_in
- cash_out
```

Los pagos:

```text
CARD
TRANSFER
```

no deben incrementar el efectivo esperado.

---

## Diferencia de caja

Una diferencia negativa:

```text
counted_cash < expected_cash
```

debe registrarse.

No debe impedir automáticamente el cierre.

Ejemplo:

```text
expected = 1500
counted  = 1400
difference = -100
```

El sistema informa la diferencia; no reemplaza la decisión administrativa posterior.

---

## Órdenes abiertas

El cierre de caja debe rechazarse cuando existan órdenes abiertas que impidan cerrar la sesión.

---

## Average Ticket

Debe verificarse el caso:

```text
orders_count == 0
```

para impedir división por cero.

Resultado esperado:

```text
average_ticket = 0
```

---

# P0 — Order Service

El testing de órdenes protege especialmente:

```text
totales
descuentos
estado
cierre
pagos
items cancelados
```

---

## Totales

Debe verificarse:

```text
subtotal =
Σ(quantity × unit_price)
```

---

## Descuentos

Debe verificarse:

```text
total = subtotal - discount
```

y:

```text
discount <= subtotal
```

---

## Descuento posterior a pagos

Un descuento no puede dejar:

```text
total < total_paid
```

Ejemplo:

```text
total original = 100
paid = 80
discount nuevo = 30
nuevo total = 70
```

Debe rechazarse.

---

## Orden cerrada

No debe permitirse modificar descuentos de una orden:

```text
CLOSED
```

---

# Matriz de estados

Los tests deben proteger explícitamente la matriz que determina el estado general de una orden.

Ejemplos ya protegidos:

```text
todos CANCELLED
→ Order CANCELLED
```

```text
IN_PROGRESS + PENDING
→ Order IN_PROGRESS
```

```text
READY + DELIVERED
→ Order READY
```

Las combinaciones de estados importantes deben mantenerse cubiertas.

---

# Cierre de orden

El cierre de una orden posee guardas críticas.

Debe rechazarse cuando:

```text
remaining > 0
```

Debe rechazarse cuando:

```text
order.items está vacío
```

Debe rechazarse cuando existen items activos no entregados.

Ejemplo:

```text
READY
```

no equivale a:

```text
DELIVERED
```

para cerrar una orden.

---

# Items CANCELLED

Los items:

```text
CANCELLED
```

no deben formar parte del subtotal cobrable.

Ejemplo:

```text
DELIVERED = 100
CANCELLED = 50
```

Resultado:

```text
subtotal = 100
```

no:

```text
150
```

Esta regla debe mantenerse como test de regresión.

---

# Pagos

Debe rechazarse:

```text
payment.amount > remaining
```

Debe requerirse caja abierta para registrar pagos cuando el flujo así lo exige.

No deben agregarse pagos sobre órdenes cerradas.

No deben eliminarse pagos de órdenes cerradas mediante el flujo normal.

---

# P1 — Autenticación

Los tests de autenticación deben proteger:

```text
token inválido
payload inválido
usuario inexistente
usuario inactivo
rol desactualizado
restaurant_id incorrecto
```

---

# Token incompleto

Un token correctamente firmado pero sin claims obligatorios debe rechazarse.

Ejemplo:

```text
sub presente
role presente
restaurant_id ausente
```

No debe producir una excepción no controlada.

Debe producir un error de dominio.

---

# Usuario inexistente

Un token no debe ser suficiente por sí mismo.

El usuario debe continuar existiendo en base de datos.

---

# Usuario inactivo

Un usuario desactivado después de emitir el token no debe continuar autenticándose únicamente porque el JWT todavía sea válido.

---

# Rol desactualizado

Si:

```text
token.role != database.user.role
```

el token debe rechazarse.

Esto fuerza una nueva autenticación y evita operar con permisos obsoletos.

---

# Multi-tenancy

Este es uno de los tests de seguridad más importantes.

Debe rechazarse:

```text
user_id válido
+
restaurant_id de otro tenant
```

La autenticación debe filtrar simultáneamente por:

```text
User.id
AND
User.restaurant_id
```

Nunca debe devolverse un usuario perteneciente a otro restaurante.

---

# Permisos

`require_roles(...)` debe probar:

```text
rol permitido
→ acceso
```

y:

```text
rol no permitido
→ DomainError
```

No es necesario levantar todo FastAPI para probar la lógica interna de autorización.

---

# P1 — Backup

Los tests de backup no intentan verificar que PostgreSQL implemente correctamente:

```text
pg_dump
pg_restore
```

Se verifica la lógica propia de Marcha alrededor de dichas herramientas.

---

# Scheduling

Debe verificarse:

```text
DAILY
WEEKLY
MONTHLY
```

incluyendo casos límite.

---

## Backup diario

Debe calcular correctamente:

```text
hoy
```

si la hora todavía no ocurrió.

Y:

```text
mañana
```

si la hora ya pasó.

---

## Backup semanal

La próxima ejecución debe coincidir con:

```text
backup_weekday
```

---

## Backup mensual

Debe manejar correctamente días inexistentes.

Ejemplo:

```text
backup_monthday = 31
```

durante febrero.

La lógica debe utilizar un día válido y no fallar.

---

# Retention Policy

La política de retención debe:

```text
eliminar backups vencidos
conservar backups recientes
```

Debe probarse también:

```text
directorio inexistente
```

sin producir error.

---

## Retención cero

La convención actual es:

```text
retention = 0
```

significa:

```text
conservar indefinidamente
```

Los tests deben dejar explícita esta semántica.

---

# Filesystem en tests

Los tests de backup utilizan:

```python
tmp_path
```

Nunca deben escribir sobre:

```text
/backups
```

real.

La regla es:

> ningún unit test puede poner en riesgo un backup real del restaurante.

---

# subprocess

Las llamadas a herramientas como:

```text
pg_dump
```

se mockean.

Se verifica:

```text
returncode = 0
→ éxito
```

y:

```text
returncode != 0
→ DomainError
```

---

# Integration Tests

Además de unit tests, Marcha debe incorporar tests con infraestructura real para aquello que SQLite no puede validar correctamente.

Estos tests deben utilizar:

```text
PostgreSQL real
Redis real cuando corresponda
FastAPI real
```

---

# Objetivos de integración

Áreas prioritarias:

```text
migraciones Alembic
foreign keys
PostgreSQL enums
transactions
locking
HTTP endpoints
authentication completa
WebSockets
Redis
backup/restore real
```

---

# Test de base vacía

Debe mantenerse un escenario capaz de demostrar:

```text
PostgreSQL vacío
   ↓
alembic upgrade head
   ↓
schema válido
   ↓
seed
   ↓
backend inicia
```

Este test protege la capacidad de instalar Marcha desde cero.

---

# Migration Tests

Toda nueva migración debe probar:

```text
upgrade
```

y, cuando sea razonable:

```text
downgrade
```

Debe comprobarse especialmente:

- creación de enums;
- eliminación explícita de enums cuando corresponda;
- foreign keys;
- defaults;
- columnas no-null;
- migración de datos.

---

# API Tests

Los endpoints críticos deben probarse también a nivel HTTP.

Áreas prioritarias:

```text
login
orders
payments
cash register
permissions
multi-tenancy
backup operations
```

Esto permite probar conjuntamente:

```text
Router
Dependencies
Service
Schemas
HTTP status
```

---

# WebSocket Tests

Los eventos críticos deben verificarse al menos mediante integración.

Casos relevantes:

```text
ITEM_READY
ORDER_UPDATED
PAYMENT_ADDED
CASH_MOVEMENT_ADDED
```

Debe comprobarse:

- evento emitido;
- audiencia correcta;
- `restaurant_id` correcto;
- station routing cuando corresponde.

---

# End-to-End

Los tests E2E deben cubrir pocos flujos, pero críticos.

Flujo principal recomendado:

```text
login
↓
abrir caja
↓
abrir mesa
↓
agregar productos
↓
enviar a cocina
↓
iniciar preparación
↓
marcar READY
↓
entregar
↓
registrar pago
↓
cerrar orden
↓
cerrar caja
```

Este flujo representa la operación central de Marcha.

---

# Test de instalación

Debe comprobarse periódicamente:

```text
máquina limpia
↓
install.sh
↓
Docker build
↓
PostgreSQL vacío
↓
Alembic
↓
seed
↓
license
↓
health
↓
login
```

---

# Test de actualización

Debe comprobarse:

```text
instalación funcional
↓
datos existentes
↓
update.sh
↓
backup pre-update
↓
git pull
↓
Docker rebuild
↓
migration
↓
restart
↓
datos preservados
```

---

# Test de desinstalación / reinstalación

Debe verificarse:

```text
uninstall
↓
reinstall
```

sin perder:

```text
database volume
backups
configuration
license
```

cuando esa sea la intención del procedimiento.

---

# Licensing Tests

El sistema de licencia debe probar:

```text
licencia válida
→ backend inicia
```

```text
firma alterada
→ backend falla
```

```text
licencia firmada para otra máquina
→ backend falla
```

```text
licencia ausente
→ instalación / arranque falla correctamente
```

---

# Backup / Restore E2E

Debe comprobarse periódicamente:

```text
crear datos conocidos
↓
backup
↓
modificar datos
↓
restore
↓
datos originales recuperados
```

Un backup que nunca fue restaurado no puede considerarse completamente validado.

---

# Tests manuales

El testing automatizado no reemplaza completamente las pruebas manuales.

Las pruebas manuales deben utilizarse especialmente para:

- UX;
- dispositivos táctiles;
- audio;
- resolución;
- Wi-Fi;
- comportamiento real del salón;
- cocina;
- caja;
- reconexión.

---

# Pilot Testing

El piloto en restaurantes reales constituye una parte fundamental de la estrategia.

Los hallazgos deben clasificarse como:

```text
BUG
FRICTION
MISSING
```

---

## BUG

El sistema hace algo incorrecto.

Ejemplo:

```text
expected_cash incorrecto
```

Debe intentar reproducirse y, cuando sea razonable:

> agregar primero un test que falle y luego corregir.

---

## FRICTION

La funcionalidad es técnicamente correcta, pero dificulta el trabajo.

Ejemplo:

```text
demasiados pasos para entregar un item
```

Puede requerir mejora de UX, no necesariamente una regla de dominio.

---

## MISSING

El flujo real requiere una capacidad inexistente.

Ejemplo:

```text
el restaurante necesita dividir una operación de una forma no contemplada
```

Debe analizarse antes de convertir automáticamente la solicitud en una nueva feature.

---

# Regression Tests

Todo bug importante corregido debe dejar, cuando sea posible, un test que reproduzca el problema.

Ejemplo actual:

```text
items CANCELLED incluidos incorrectamente en subtotal
```

Una vez corregido:

```text
test_calculate_totals_excluye_items_cancelados
```

impide reintroducir accidentalmente el defecto.

> Un bug crítico arreglado sin test es un bug que puede volver silenciosamente.

---

# Tests y reglas de dominio

Los tests deben reflejar las reglas documentadas en:

```text
domain_rules.md
```

Cuando se modifica una regla del dominio:

1. revisar tests existentes;
2. modificar o agregar tests;
3. modificar Service;
4. actualizar documentación.

---

# Naming de tests

Los nombres deben describir claramente:

```text
acción
+
condición
+
resultado esperado
```

Ejemplos:

```python
test_add_payment_rechaza_si_excede_saldo_restante
```

```python
test_close_cash_register_bloquea_si_hay_ordenes_abiertas
```

```python
test_authenticate_token_rechaza_restaurant_id_cruzado
```

Los nombres largos son aceptables cuando mejoran la comprensión.

---

# Comentarios en tests

Los comentarios deben explicar principalmente:

- por qué existe el caso;
- qué bug protege;
- qué comportamiento de negocio queda fijado.

Ejemplo útil:

```text
La tarjeta suma a ventas pero no al efectivo esperado.
```

Esto tiene más valor que comentar cada línea del test.

---

# Arrange / Act / Assert

Los tests pueden seguir conceptualmente:

```text
Arrange
Act
Assert
```

No es obligatorio escribir esos encabezados.

Debe mantenerse visualmente clara la separación entre:

```text
preparación
operación
verificación
```

---

# Un comportamiento por test

Cada test debería proteger principalmente una regla.

Evitar tests gigantes que comprueben veinte condiciones sin identificar cuál falló.

Excepción:

```text
tests end-to-end
```

donde el objetivo es validar un flujo completo.

---

# Tests de métodos privados

Actualmente algunos tests verifican métodos como:

```text
_calculate_totals
_calculate_order_status
_calculate_next_run
_apply_retention_policy
```

Esto es aceptable cuando:

- representan lógica crítica y estable;
- son esencialmente funciones de dominio internas;
- probarlas directamente produce tests simples y precisos.

No debe asumirse que todo método privado requiere tests directos.

El comportamiento público continúa siendo prioritario.

---

# Pydantic

Cuando una validación pertenece al Schema, debe probarse en ese nivel.

Ejemplo:

```text
counted_cash >= 0
```

Si Pydantic garantiza la condición, el Service no necesita ser el único lugar donde se pruebe.

Estos tests también permiten detectar validaciones duplicadas o código muerto.

---

# Mocks

Se utilizan mocks cuando la dependencia externa no forma parte del comportamiento que se desea probar.

Buenos candidatos:

```text
subprocess
SMTP
filesystem externo
servicios externos
```

No debe mockearse tanto que el test termine comprobando únicamente los mocks.

---

# Coverage

La cobertura puede utilizarse como indicador.

No debe convertirse en objetivo independiente.

Un:

```text
95% coverage
```

puede seguir dejando sin probar una transición crítica de caja.

Un:

```text
70% coverage
```

puede ser mucho más valioso si protege todas las operaciones P0.

La prioridad es:

```text
risk coverage
```

no:

```text
line coverage
```

---

# Ejecución habitual

Toda la suite:

```bash
pytest -v
```

Solo unit tests:

```bash
pytest tests/unit -v
```

Archivo específico:

```bash
pytest tests/unit/test_order_service.py -v
```

Desde Docker:

```bash
docker compose exec backend pytest -v
```

---

# Cuándo ejecutar tests

Durante desarrollo:

```text
tests relacionados con el módulo modificado
```

Antes de commit importante:

```text
unit suite completa
```

Antes de release:

```text
unit
integration
build frontend
migration
installation/update checks
critical E2E
```

---

# Criterio de release

Una versión no debe considerarse lista únicamente porque:

```text
"funciona en mi PC"
```

Como mínimo debe comprobarse:

```text
tests P0 OK
tests P1 críticos OK
frontend build OK
Alembic OK
startup OK
health OK
flujo operativo crítico OK
backup disponible
```

---

# Testing en piloto

Durante la etapa de piloto, el criterio práctico más importante es completar un turno real sin intervención técnica.

Flujo esperado:

```text
abrir caja
↓
trabajar durante el turno
↓
tomar pedidos
↓
producir
↓
entregar
↓
cobrar
↓
cerrar órdenes
↓
cerrar caja
↓
generar backup
```

sin necesidad de:

```text
terminal
Docker CLI
DBeaver
modificar DB manualmente
editar código
```

---

# Evolución de la suite

La suite debe crecer a partir de:

```text
riesgos conocidos
bugs encontrados
reglas nuevas
incidencias de pilotos
cambios de arquitectura
```

No es necesario intentar cubrir todo Marcha de una sola vez.

Prioridad recomendada:

```text
P0 dinero / estado
↓
P1 seguridad / recuperación
↓
API / integración
↓
E2E crítico
↓
P2 administración / UX
```

---

# Documentación relacionada

```text
domain_rules.md
data_model.md
realtime_events.md
backend_standards.md
development_setup.md
```

---

# Principio final

Cada test importante debería responder:

> ¿Qué daño evita que vuelva a ocurrir?

Si la respuesta es clara, probablemente sea un test valioso.

Para Marcha, los tests prioritarios son aquellos que garantizan que:

```text
el pedido conserva un estado válido,
el cliente paga lo correcto,
la caja calcula correctamente,
un restaurante nunca accede a otro,
los datos pueden recuperarse,
y una actualización no rompe una instalación funcional.
```