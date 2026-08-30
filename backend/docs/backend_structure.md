# Backend Structure

## Objetivo

El backend de Marcha está organizado mediante una arquitectura por capas orientada a dominio.

Sus objetivos principales son:

- separar responsabilidades;
- mantener el código fácil de comprender y mantener;
- evitar lógica de negocio dentro de los routers;
- facilitar el testing;
- reutilizar lógica desde distintos endpoints;
- mantener aisladas las reglas de negocio de los detalles HTTP;
- centralizar las operaciones que afectan múltiples entidades;
- mantener una estructura consistente entre los distintos módulos del sistema.

La regla principal es:

> Los routers gestionan HTTP.  
> Los Services implementan las reglas del negocio.

---

## Estructura general

La estructura principal del backend es:
```text
app/
├── core/
├── db/
├── dependencies/
├── domain/
├── infrastructure/
├── models/
├── routers/
├── scheduler/
├── schemas/
├── services/
├── utils/
├── websocket/
├── main.py
└── seed.py
```

Algunos módulos pueden tener archivos adicionales cuando una funcionalidad lo requiere.

Por ejemplo:
```text
domain/
├── order/
├── cash_register/
├── stations/
├── products/
└── ...
```
La estructura puede evolucionar, pero las responsabilidades de cada capa deben mantenerse.

## Flujo general de una operación

Una operación HTTP típica sigue este recorrido:
```text
Cliente
   ↓
Router
   ↓
Dependency Injection
   ↓
Service
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

Cuando corresponde, el Service también puede interactuar con:

- Redis
- WebSockets
- otros Services
- sistemas de backup
- servicios de infraestructura

Actualmente no existe la obligación de utilizar una capa Repository independiente.

Los Services pueden consultar directamente `SQLAlchemy` cuando la operación lo requiere.

Si en el futuro se introduce una capa `Repository`, deberá hacerse como una decisión arquitectónica explícita y no de manera parcial o inconsistente.

## Routers

Los routers representan exclusivamente la capa HTTP de la aplicación.

Sus responsabilidades son:

- definir endpoints;
- declarar métodos HTTP;
- definir schemas de entrada y salida;
- recibir parámetros;
- resolver dependencias mediante Depends;
- validar permisos y roles mediante dependencias;
- invocar el Service correspondiente;
- devolver la respuesta HTTP apropiada.

Ejemplo conceptual:

```text
POST /orders/{id}/payments
        ↓
Router
        ↓
OrderService
        ↓
reglas de negocio
        ↓
SQLAlchemy
```

Un router no debe contener lógica de negocio.

Por ejemplo, un router no debería decidir:

- si una orden puede cerrarse
- si un pago supera el saldo
- si una caja está abierta
- si un item puede cambiar de estado

Estas decisiones pertenecen al dominio.

## Domain

La carpeta `domain/` contiene la lógica de negocio organizada por área funcional.

Ejemplo:

```text
domain/
└── product/
    ├── dependencies.py
    └── product_service.py
```

Otros dominios pueden incluir archivos adicionales según su complejidad.

Los Services del dominio conocen las reglas del negocio.

Ejemplos:

- evitar duplicados;
- validar transiciones de estado;
- calcular totales;
- validar descuentos;
- controlar pagos;
- cerrar órdenes;
- abrir o cerrar caja;
- cancelar items;
- emitir eventos;
- modificar varias entidades dentro de una misma operación.

El dominio no debería depender de detalles de presentación del frontend.

## Services

Los Services constituyen la capa principal de lógica de negocio.

Sus responsabilidades pueden incluir:

- consultar Models mediante `SQLAlchemy`;
- crear y modificar entidades;
- ejecutar validaciones de dominio;
- calcular valores derivados;
- coordinar varias operaciones;
- reutilizar otros Services;
- emitir eventos;
- ejecutar commits o rollbacks cuando corresponda;
- lanzar `DomainError`;
- transformar entidades cuando la operación lo requiera.

Ejemplo:

```python
class ProductService:

    def __init__(self, db: Session):
        self.db = db

    def create_product(
        self,
        restaurant_id: int,
        data: ProductCreate
    ):
        ...
```

Un Service debe recibir explícitamente las dependencias que necesita.

No debe crear conexiones a base de datos por su cuenta.

## Dependencias

La inyección de dependencias se utiliza para crear Services y proporcionar recursos compartidos.

Ejemplo:

```python
def get_product_service(
    db: Session = Depends(get_db)
):
    return ProductService(db)
```

El router recibe entonces el Service:

```python
service: ProductService = Depends(
    get_product_service
)
```

FastAPI resuelve automáticamente la cadena:

```text
Router
   ↓
get_product_service()
   ↓
get_db()
   ↓
ProductService(db)
```

Los routers no deberían instanciar Services directamente:

```python
ProductService(db)
```
si ya existe una dependencia destinada a hacerlo.

Esto mantiene consistente la creación de dependencias y facilita testing y sustitución de implementaciones.

## Models

Los Models representan la estructura persistente almacenada en la base de datos mediante `SQLAlchemy`.

Ejemplo:

- User
- Restaurant
- Table
- Order
- OrderItem
- Product
- Category
- ProductionStation
- Payment
- CashRegister
- CashMovement

Sus responsabilidades principales son:

- definir columnas;
- definir relaciones;
- definir constraints;
- representar las entidades persistidas.

Los Models no son la API pública del backend.

Un Model no debería utilizarse directamente como contrato HTTP salvo que exista una razón explícita.

La lógica de negocio debe permanecer en los Services.

## Schemas

Los Schemas representan los datos que entran y salen de la API.

Se implementan mediante `Pydantic`.

No tienen por qué coincidir exactamente con los Models.

Es habitual separar:

- Create
- Update
- Response
- Detail
- Summary

Ejemplo:

- ProductCreate
- ProductUpdate
- ProductResponse

Un Schema puede incluir campos que no existen físicamente como columnas.

Por ejemplo:

- subtotal
- discount
- total
- remaining
- product_name
- table_number

Estos valores pueden ser calculados o construidos por el backend para facilitar el consumo de la API.

## DB

La carpeta `db/` contiene los elementos relacionados con acceso y configuración de la base de datos.

Normalmente incluye:

- creación de Engine;
- SessionLocal;
- get_db;
- configuración `SQLAlchemy`;
- Base declarativa.

La aplicación utiliza `PostgreSQL` en producción.

La evolución del esquema se realiza mediante `Alembic`.

Los Services reciben una `Session` y operan sobre ella.

## Core

La carpeta `core/` contiene componentes transversales que no pertenecen a un dominio concreto.

Por ejemplo pueden incluir:

- configuración;
- autenticación;
- seguridad;
- utilidades globales;
- configuración de logging.

No debe utilizarse como una carpeta genérica donde colocar cualquier archivo que no tenga ubicación clara.

## Infrastructure

La carpeta `infrastructure/` contiene implementaciones relacionadas con el entorno técnico de ejecución y no directamente con reglas del negocio.

Ejemplo actual:

```text
infrastructure/
└── licensing/
    ├── machine_fingerprint.py
    ├── license_service.py
    ├── validate_license.py
    └── public_key.pem
```

Esta capa puede contener integraciones o mecanismos técnicos específicos de infraestructura.

La lógica de negocio principal no debe trasladarse aquí.

## Scheduler

La carpeta `scheduler/` contiene tareas programadas ejecutadas por el backend.

Ejemplo:

```text
scheduler/
└── backup_jobs.py
```

Estas tareas pueden invocar Services existentes.

No deberían duplicar reglas de negocio.

Ejemplo:

```text
Scheduler
   ↓
BackupService
   ↓
operación de backup
```

## Eventos

Marcha utiliza eventos para mantener sincronizados los distintos clientes.

Los eventos pueden utilizar:

- WebSockets;
- Redis;
- eventos persistidos;
- distribución por rol;
- distribución por estación.

Los eventos se generan desde los Services.

Nunca desde los Routers.

Ejemplo:

```text
Waiter
   ↓
HTTP
   ↓
OrderService
   ↓
modifica OrderItem
   ↓
commit
   ↓
emite ITEM_STATUS_CHANGED
   ↓
Redis / WebSocket
   ↓
Kitchen / Cashier / Waiter
```

Esto permite que el evento represente una operación de negocio realmente ejecutada y no simplemente una petición HTTP recibida.

## Manejo de errores

Las reglas de negocio que no pueden cumplirse generan: `DomainError` acompañado de un: `ErrorCode`

Ejemplo conceptual:

```text
raise DomainError(
    "La caja no esta abierta",
    ErrorCode.CASH_REGISTER_NOT_OPEN
)
```

Los routers no deberían utilizar `try/except` para traducir individualmente estos errores.

Los `handlers` globales de FastAPI son responsables de convertirlos en respuestas HTTP.

Flujo:

```text
Service
   ↓
DomainError
   ↓
Exception Handler
   ↓
HTTP response
   ↓
Frontend
```

## Multi-tenancy

Marcha soporta múltiples restaurantes a nivel de modelo de datos.

Las operaciones relacionadas con datos de negocio deben estar acotadas por: `restaurant_id`

Siempre que una entidad pertenezca a un restaurante, las consultas deben verificar dicha pertenencia.

Ejemplo:

```python
.filter(
    Product.id == product_id,
    Product.restaurant_id == restaurant_id
)
```

No debe confiarse únicamente en IDs recibidos desde el cliente.

Esta regla constituye también una frontera de seguridad entre restaurantes.

## Transacciones

Una operación de negocio puede modificar varias entidades.

Ejemplo:

```text
agregar pago
    ↓
Payment
Order
CashRegister
DomainEvent
```

Todas las modificaciones que forman parte de una misma operación lógica deben mantenerse coherentes.

El Service es responsable de determinar cuándo debe ejecutarse el `commit`.

Los routers no deben realizar `commits`.

## Dependencias permitidas

Como regla general:

```text
Router
  ↓
Service
  ↓
Model / DB
```

También son válidas relaciones como:

```text
Service
  ↓
otro Service

Service
  ↓
Infrastructure

Scheduler
  ↓
Service
```

Debe evitarse:

```text
Model
  ↓
Router

Model
  ↓
Service

Service
  ↓
Router

Domain
  ↓
Frontend
```

Las dependencias deben apuntar hacia las capas que implementan detalles necesarios, evitando dependencias circulares.

## Principios generales

El Router responde a:

> ¿Qué quiere hacer el cliente?

El Service responde a:

> ¿Cómo debe ejecutarse correctamente esa operación?

El Model responde a:

> ¿Cómo se persiste esta información?

El Schema responde a:

> ¿Qué información entra o sale de la API?

Infrastructure responde a:

> ¿Qué mecanismo técnico permite ejecutar determinadas capacidades?

## Regla final

Cuando se implementa una nueva funcionalidad, debería ser posible identificar claramente:

```text
Router
↓
Schema
↓
Dependency
↓
Service
↓
Models
↓
Eventos / infraestructura cuando corresponda
```

Si una regla de negocio comienza a aparecer en un Router, un Model o un componente de infraestructura, probablemente se encuentra en la capa incorrecta.