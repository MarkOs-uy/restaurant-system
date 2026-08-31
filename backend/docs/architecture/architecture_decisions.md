# Architecture Decisions

Este documento registra decisiones arquitectónicas y de diseño tomadas durante el desarrollo de Marcha.

Su objetivo es conservar el contexto de decisiones importantes para evitar que futuras modificaciones eliminen restricciones o comportamientos que fueron introducidos deliberadamente.

Cada decisión debería documentar:

- contexto;
- decisión;
- motivo;
- consecuencias;
- alternativas descartadas cuando corresponda.

Las decisiones aceptadas no deben modificarse sin una justificación clara.

---

## ADR-001 — Arquitectura LAN y operación offline-first

**Estado:** Aceptada

### Contexto

Marcha está pensado para operar dentro de la red local de un restaurante.

La operación diaria no debe depender de una conexión a Internet disponible o estable.

### Decisión

El sistema funciona mediante una arquitectura local:

```text
Dispositivos del restaurante
        ↓
Red LAN / Wi-Fi
        ↓
Servidor Marcha
        ↓
PostgreSQL / Redis
```

El frontend, backend y servicios principales se ejecutan dentro de la infraestructura local del restaurante.

### Motivo

La conectividad a Internet no puede considerarse un requisito confiable durante la operación de un restaurante.

La toma de pedidos, producción, entrega y cobro deben continuar funcionando aunque se pierda la conexión externa.

### Consecuencias

- Marcha puede operar sin Internet.
- Los dispositivos deben estar conectados a la misma red local.
- El servidor local se convierte en un componente crítico de la operación.
- Instalación, backup y recuperación deben poder realizarse localmente.
- Funcionalidades externas, como correo electrónico, pueden degradarse sin afectar la operación principal.

---

## ADR-002 — PostgreSQL como base de datos de producción

**Estado:** Aceptada

### Decisión

PostgreSQL es el motor de base de datos utilizado en producción.

### Motivo

Se necesita una base de datos relacional capaz de proporcionar:

- transacciones;
- integridad referencial;
- concurrencia;
- constraints;
- estabilidad;
- backups y restauración confiables.

### Consecuencias

- Los despliegues de producción incluyen PostgreSQL.
- Las operaciones de backup utilizan herramientas compatibles con PostgreSQL.
- La evolución del esquema debe mantenerse compatible con PostgreSQL.

---

## ADR-003 — Alembic es la única autoridad para evolucionar el esquema

**Estado:** Aceptada

### Contexto

Durante una etapa anterior del desarrollo se utilizó `Base.metadata.create_all()` para crear tablas.

Posteriormente se detectaron inconsistencias al restaurar backups y evolucionar el esquema mediante Alembic.

### Decisión

Toda modificación del esquema de base de datos se realiza exclusivamente mediante Alembic.

No se utiliza:

```python
Base.metadata.create_all()
```

para crear ni actualizar el esquema de producción.

### Motivo

El esquema debe poder reproducirse de manera determinista desde una base de datos vacía.

Alembic permite:

- versionar cambios;
- revisar migraciones;
- reproducir instalaciones;
- actualizar instalaciones existentes;
- realizar downgrades cuando sea posible.

### Consecuencias

El flujo de modificación del esquema es:

```text
Models
   ↓
alembic revision --autogenerate
   ↓
revisión manual
   ↓
alembic upgrade head
```

Las migraciones generadas automáticamente nunca deben asumirse correctas sin revisión.

---

## ADR-004 — Lógica de negocio centralizada en Services

**Estado:** Aceptada

### Decisión

Los Routers gestionan HTTP.

Los Services implementan las reglas de negocio.

Flujo habitual:

```text
Router
   ↓
Service
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

### Motivo

Centralizar las reglas de negocio evita:

- duplicación;
- diferencias entre endpoints;
- lógica HTTP mezclada con dominio;
- dificultad para reutilizar operaciones.

### Consecuencias

Los Routers no deben:

- realizar consultas complejas;
- decidir transiciones de estado;
- calcular reglas de negocio;
- realizar `commit`.

Los Services pueden coordinar múltiples entidades y emitir eventos.

---

## ADR-005 — No existe una capa Repository obligatoria

**Estado:** Aceptada

### Contexto

El backend utiliza SQLAlchemy directamente desde los Services.

### Decisión

No se introduce una capa Repository únicamente por seguir un patrón arquitectónico.

Los Services pueden consultar SQLAlchemy directamente.

### Motivo

En el estado actual del sistema, una capa adicional añadiría complejidad y delegación sin aportar suficiente valor.

### Consecuencias

El flujo actual es:

```text
Router
   ↓
Service
   ↓
SQLAlchemy / Models
```

Si en el futuro se introduce Repository Pattern, deberá hacerse como una decisión arquitectónica explícita y consistente.

---

## ADR-006 — Multi-tenancy mediante `restaurant_id`

**Estado:** Aceptada

### Decisión

Las entidades que pertenecen a un restaurante se identifican mediante `restaurant_id`.

Las consultas deben incluir esa pertenencia siempre que corresponda.

Ejemplo:

```python
.filter(
    Product.id == product_id,
    Product.restaurant_id == restaurant_id
)
```

### Motivo

No debe ser posible acceder a recursos de otro restaurante únicamente conociendo su ID.

### Consecuencias

`restaurant_id` funciona tanto como:

- criterio de partición lógica;
- regla de negocio;
- frontera de seguridad.

---

## ADR-007 — Errores de dominio mediante `DomainError` + `ErrorCode`

**Estado:** Aceptada

### Decisión

Las reglas de negocio que no pueden cumplirse generan:

```text
DomainError
+
ErrorCode
```

Los Services no lanzan `HTTPException`.

### Motivo

Los errores de negocio no deberían depender del protocolo HTTP.

### Consecuencias

El flujo es:

```text
Service
   ↓
DomainError
   ↓
Exception Handler
   ↓
HTTP Response
   ↓
Frontend
```

Esto permite que el frontend interprete errores mediante códigos estables.

---

## ADR-008 — Los eventos se generan desde Services

**Estado:** Aceptada

### Decisión

Los eventos de negocio se emiten desde los Services y nunca desde los Routers.

### Motivo

Un evento debe representar una operación de negocio efectivamente ejecutada, no simplemente una petición HTTP recibida.

### Consecuencias

Los eventos pueden ser consumidos por:

- Waiter;
- Kitchen;
- Cashier;
- Admin;

mediante WebSockets y Redis.

---

## ADR-009 — Estaciones de producción

**Estado:** Aceptada

### Contexto

Los productos pueden estar asociados a estaciones de producción.

Ejemplos habituales:

```text
Cocina
Barra
Parrilla
```

### Decisión

Se establecen las siguientes reglas:

- los mozos no consultan estaciones;
- cocina consulta únicamente estaciones activas;
- las estaciones no se eliminan físicamente;
- las estaciones se activan o desactivan;
- el nombre de una estación nunca puede ser nulo.

### Motivo

Las estaciones forman parte de la configuración histórica de productos y producción.

Eliminar una estación podría afectar referencias existentes o datos históricos.

### Consecuencias

La eliminación se modela mediante desactivación lógica.

Una estación inactiva deja de utilizarse operativamente, pero continúa existiendo en la base de datos.

---

## ADR-010 — Convenciones HTTP para respuestas

**Estado:** Aceptada

### Decisión

Las respuestas HTTP siguen estas convenciones generales.

### GET

Siempre devuelve el recurso o colección solicitada.

### POST

Devuelve el recurso creado.

Habitualmente:

```text
201 Created
```

### PATCH

Devuelve el recurso actualizado cuando el cliente necesita utilizar inmediatamente esa representación.

Si el cliente realiza posteriormente un `GET` y no necesita el recurso actualizado como respuesta, puede utilizarse:

```text
204 No Content
```

### DELETE

Cuando la operación no devuelve contenido:

```text
204 No Content
```

No se utilizan respuestas artificiales como:

```json
{
  "ok": true
}
```

### Motivo

Mantener respuestas consistentes facilita el consumo de la API y reduce comportamientos especiales en el frontend.

---

## ADR-011 — Cancelación física y lógica de items

**Estado:** Aceptada

### Contexto

Un item puede encontrarse en distintas etapas del flujo de producción.

### Decisión

Un item en estado `PENDING` puede eliminarse físicamente.

Una vez enviado a producción, la cancelación debe conservar el historial y realizarse de forma lógica.

Un item `DELIVERED` no puede cancelarse mediante el flujo normal.

### Motivo

Después de enviar un producto a producción, su existencia forma parte de la historia operativa del pedido.

Eliminarlo físicamente destruiría información relevante.

### Consecuencias

Se diferencia entre:

```text
PENDING
→ eliminación física

SENT / IN_PROGRESS / READY
→ cancelación lógica
```

---

## ADR-012 — Nginx como punto de entrada HTTP en producción

**Estado:** Aceptada

### Decisión

En producción, Nginx es el único servicio HTTP expuesto a la red local.

Flujo:

```text
Cliente
   ↓
Nginx :80
   ├── /        → React
   ├── /api     → FastAPI
   └── /ws      → WebSocket
```

FastAPI no expone directamente su puerto a la LAN.

### Motivo

Esto permite:

- un único punto de acceso;
- simplificar URLs del frontend;
- proxy de WebSockets;
- desacoplar puertos internos;
- servir el frontend de producción.

---

## ADR-013 — Docker Compose como mecanismo de despliegue

**Estado:** Aceptada

### Decisión

Los servicios de producción se ejecutan mediante Docker Compose.

Actualmente incluye:

- PostgreSQL;
- backend;
- Redis;
- frontend/Nginx.

### Motivo

El despliegue debe ser reproducible y mantener aisladas las dependencias del sistema.

### Consecuencias

Los scripts de instalación, actualización, inicio y detención operan sobre el mismo `docker-compose.prod.yml`.

---

## ADR-014 — Systemd como propietario lógico del stack

**Estado:** Aceptada

### Contexto

Docker Compose puede iniciar contenedores correctamente aunque posteriormente uno de ellos falle.

### Decisión

`systemd` administra el ciclo de vida lógico del stack de producción.

El servicio se considera iniciado únicamente cuando el backend responde correctamente.

### Motivo

No debe confundirse:

```text
contenedor creado
```

con:

```text
aplicación operativa
```

### Consecuencias

Un fallo de arranque del backend provoca un estado `failed` del servicio en lugar de anunciar falsamente que Marcha está operativo.

---

## ADR-015 — Backups administrados por Marcha

**Estado:** Aceptada

### Decisión

Marcha gestiona internamente sus backups.

El sistema soporta:

- backups manuales;
- backups automáticos;
- retención;
- backups previos a restauración;
- restauración;
- descarga;
- eliminación;
- envío por correo cuando está configurado.

### Motivo

El sistema anterior basado en un contenedor externo de backup resultaba redundante una vez implementada la funcionalidad completa dentro de Marcha.

### Consecuencias

No existe un servicio Docker independiente exclusivamente para backups.

---

## ADR-016 — Licencia offline firmada mediante Ed25519

**Estado:** Aceptada

### Contexto

Marcha debe poder licenciarse sin depender de servicios externos ni conexión a Internet.

### Decisión

La licencia se almacena en:

```text
/var/lib/pos-restaurant/license.json
```

y contiene información firmada mediante Ed25519.

El backend dispone únicamente de la clave pública.

La clave privada nunca forma parte de la aplicación distribuida.

### Motivo

Se necesita verificar autenticidad sin necesidad de contactar un servidor externo.

### Consecuencias

El backend valida la licencia durante el arranque.

Si la firma es inválida, la aplicación no inicia.

---

## ADR-017 — Licencia vinculada a la máquina

**Estado:** Aceptada

### Decisión

La licencia está asociada a un fingerprint calculado a partir de identificadores estables del host.

Actualmente intervienen:

```text
/etc/machine-id
/sys/class/dmi/id/product_uuid
```

Los identificadores se normalizan y procesan mediante SHA-256.

### Motivo

Copiar el archivo de licencia a otra máquina no debe permitir ejecutar automáticamente otra instalación.

### Consecuencias

El fingerprint siempre se recalcula desde el host.

No se confía en un archivo local que contenga la identidad de la máquina.

---

## ADR-018 — La clave privada de licencias se mantiene fuera del proyecto distribuido

**Estado:** Aceptada

### Decisión

Las herramientas de emisión de licencias viven en un proyecto privado independiente.

Ejemplo:

```text
marcha-license-tools/
```

La clave privada:

- no se copia al servidor del restaurante;
- no forma parte de las imágenes Docker;
- no forma parte del repositorio distribuido;
- no se almacena junto al backend.

### Motivo

Quien posea la clave privada puede emitir licencias válidas.

Debe mantenerse separada de cualquier componente entregado al cliente.

---

## ADR-019 — Contraseña SMTP cifrada en reposo

**Estado:** Aceptada

### Decisión

La contraseña SMTP se almacena cifrada mediante Fernet.

La clave de cifrado se obtiene desde:

```text
ENCRYPTION_KEY
```

en `backend/.env`.

### Motivo

Las credenciales SMTP no deben almacenarse en texto plano en PostgreSQL.

### Consecuencias

`ENCRYPTION_KEY` debe conservarse junto con la instalación.

Restaurar una base de datos sin la clave correspondiente impediría descifrar las credenciales almacenadas.

---

# Incorporación de nuevas decisiones

Cuando se tome una decisión que afecte significativamente:

- arquitectura;
- persistencia;
- seguridad;
- despliegue;
- reglas estructurales del dominio;
- interoperabilidad;
- compatibilidad futura;

debe añadirse una nueva ADR.

Las decisiones no deberían reescribirse para ocultar la historia.

Si una decisión cambia, se recomienda:

1. marcar la ADR anterior como `Reemplazada`;
2. crear una nueva ADR;
3. indicar qué decisión reemplaza;
4. documentar el motivo del cambio.