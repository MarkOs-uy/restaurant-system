# Backend Coding Standards

Proyecto: Marcha  
Lenguaje: Python 3.13  
Framework: FastAPI  
ORM: SQLAlchemy 2.x  
Migraciones: Alembic

Este documento define las convenciones de desarrollo utilizadas en el backend de Marcha.

Su objetivo es mantener un código:

- consistente;
- predecible;
- legible;
- fácil de mantener;
- fácil de revisar;
- alineado con la arquitectura definida en `backend_structure.md`.

---

## Arquitectura

Se utiliza una arquitectura por capas.

El flujo habitual es:

```text
Router
   ↓
Service
   ↓
SQLAlchemy / Models
   ↓
PostgreSQL
```

Cuando corresponde, un `Service` también puede interactuar con otros Services, eventos o componentes de infraestructura.

> Nunca se coloca lógica de negocio en los Routers.

La arquitectura detallada se documenta en `backend_structure.md`.

---

## Routers

Los Routers representan exclusivamente la capa HTTP.

Cada archivo de Router debe contener, cuando corresponda:

- docstring inicial del módulo;
- instancia de `APIRouter`;
- endpoints claramente separados;
- `summary`;
- `description`;
- `response_model`;
- `status_code` explícito.

Ejemplo:

```python
@router.get(
    "/",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías",
    description="Devuelve las categorías del restaurante."
)
```

Los Routers deben limitarse a:

- recibir parámetros;
- resolver dependencias;
- validar permisos;
- invocar Services;
- devolver respuestas HTTP.

> Un Router no debe decidir reglas de negocio.

---

## Comentarios y separación visual

Los endpoints pueden separarse mediante encabezados visuales:

```python
# ----------------------------------------------------------------------------------------------------
# Listar categorías
# ----------------------------------------------------------------------------------------------------
```

Estos comentarios deben utilizarse únicamente para mejorar la navegación dentro de archivos extensos.

No deben sustituir nombres claros de funciones ni una estructura adecuada del código.

---

## Dependency Injection

Se utiliza Dependency Injection para proporcionar Services y recursos compartidos.

Correcto:

```python
service: ProductService = Depends(get_product_service)
```

Incorrecto:

```python
service = ProductService(db)
```

Los Routers no deben instanciar Services directamente cuando existe una dependencia definida para ello.

Las dependencias de cada dominio deben centralizar la creación de sus Services.

Ejemplo:

```python
def get_product_service(
    db: Session = Depends(get_db)
) -> ProductService:
    return ProductService(db)
```

Esto facilita:

- testing;
- sustitución de dependencias;
- consistencia;
- reutilización.

---

## Response Models

Siempre que un endpoint devuelva un recurso con estructura conocida debe utilizar `response_model`.

Ejemplos:

```text
ProductResponse
CategoryResponse
OrderResponse
CashMovementResponse
```

Puede omitirse cuando la respuesta no corresponde a un Schema convencional, por ejemplo:

- descarga de archivos;
- `StreamingResponse`;
- `Response`;
- respuestas completamente dinámicas;
- endpoints cuya salida depende de contenido no estructurado.

Cuando una respuesta dinámica comienza a adquirir una estructura estable, debe evaluarse la creación de un Schema específico.

---

## Status Codes

Los códigos HTTP deben declararse explícitamente cuando el endpoint tenga un código esperado distinto o relevante para su semántica.

Convenciones habituales:

```text
200 OK
Consulta o actualización exitosa.

201 Created
Creación exitosa.

204 No Content
Operación exitosa sin cuerpo de respuesta.
```

Los endpoints `DELETE` que no devuelvan contenido deben utilizar:

```python
status_code=status.HTTP_204_NO_CONTENT
```

y no devolver estructuras como:

```json
{
  "ok": true
}
```

---

## HTTPException

Las validaciones de negocio deben realizarse en los Services.

Los Services:

```text
NO lanzan HTTPException
```

El Router únicamente puede utilizar `HTTPException` cuando el error pertenece específicamente a la capa HTTP.

Las reglas de dominio deben representarse mediante:

```text
DomainError
+
ErrorCode
```

La traducción a respuesta HTTP corresponde a los Exception Handlers globales.

---

## Schemas

Los Schemas representan contratos de entrada y salida de la API.

Se utilizan nombres explícitos según su responsabilidad.

Convención habitual:

```text
ProductCreate
ProductUpdate
ProductResponse
ProductSummary
ProductDetail
```

No debe reutilizarse un Schema de entrada como Schema de salida únicamente para evitar crear otro tipo.

Por ejemplo:

```text
ProductCreate
```

no debe utilizarse como respuesta si el recurso devuelto contiene campos adicionales como:

```text
id
created_at
active
```

Los Schemas base, como `EntityBase`, sólo deben introducirse cuando exista una cantidad significativa de campos realmente compartidos.

Si dos Schemas comparten únicamente uno o dos atributos, se prefiere repetirlos para mantener las estructuras explícitas y simples.

---

## Services

Los Services contienen la lógica de negocio.

Como guía general, un Service puede organizarse en este orden:

1. `__init__`
2. helpers privados;
3. operaciones de consulta;
4. operaciones CRUD;
5. métodos especializados.

No es obligatorio seguir este orden cuando otro agrupamiento mejora claramente la legibilidad.

Los Services pueden:

- realizar consultas SQLAlchemy;
- crear y modificar Models;
- validar reglas de negocio;
- coordinar varias entidades;
- reutilizar otros Services;
- emitir eventos;
- ejecutar `commit`;
- ejecutar `rollback` cuando corresponda;
- lanzar `DomainError`;
- devolver Models o Schemas tipados.

Los Services:

- nunca lanzan `HTTPException`;
- nunca dependen de detalles HTTP;
- nunca dependen del frontend;
- son responsables de mantener coherentes las operaciones de negocio.

> Los Routers nunca realizan `commit`.

---

## Retorno de Services

Siempre que sea razonable, los métodos de Service deben devolver:

- Models SQLAlchemy;
- Schemas Pydantic;
- tipos explícitos.

Se deben evitar diccionarios anónimos (`dict`) cuando la estructura de la respuesta sea estable.

Los diccionarios pueden utilizarse en casos realmente dinámicos, por ejemplo:

- dashboards;
- reportes;
- agregaciones;
- estructuras variables.

Si una estructura dinámica se vuelve estable y reutilizada, debe convertirse en un Schema tipado.

---

## Nomenclatura de métodos

Los métodos públicos deben utilizar nombres descriptivos y consistentes.

Convenciones habituales:

```text
get_xxx()
list_xxx()
create_xxx()
update_xxx()
delete_xxx()
toggle_xxx()
```

Los métodos privados comienzan con `_`.

Ejemplo:

```python
def _calculate_totals(...):
    ...
```

La nomenclatura debe expresar la intención de la operación y no únicamente el mecanismo utilizado.

---

## SQLAlchemy

Las consultas SQLAlchemy deben escribirse con formato multilínea cuando tengan más de una condición o resulten difíciles de leer en una sola línea.

Ejemplo:

```python
product = (
    self.db.query(Product)
    .filter(
        Product.id == product_id,
        Product.restaurant_id == restaurant_id
    )
    .first()
)
```

Las consultas relacionadas con entidades pertenecientes a un restaurante deben incluir siempre el `restaurant_id` correspondiente.

> No debe confiarse únicamente en un ID recibido desde el cliente para determinar pertenencia.

---

## Transacciones

El `Service` es responsable de determinar los límites de una operación de negocio.

Cuando una operación modifica varias entidades relacionadas, debe mantenerse su consistencia dentro de la misma unidad lógica.

Ejemplo:

```text
agregar pago
   ↓
Payment
Order
CashRegister
DomainEvent
```

El `commit` debe ejecutarse únicamente cuando la operación completa haya sido validada correctamente.

Los Routers no ejecutan `commit`.

---

## Models

Los Models representan la persistencia mediante SQLAlchemy.

Sus responsabilidades son:

- definir columnas;
- definir relaciones;
- definir constraints;
- representar entidades persistidas.

Los Models no deben contener reglas de negocio.

No deben utilizarse como sustituto de los Services.

---

## Nombres de archivos

### Routers

```text
category.py
product.py
table.py
order.py
```

### Services

```text
product_service.py
table_service.py
order_service.py
```

### Dependencias

```text
dependencies.py
```

### Schemas

Los nombres de clases deben ser explícitos:

```text
ProductCreate
ProductUpdate
ProductResponse
ProductDetail
ProductSummary
```

---

## Errores de dominio

Los Services lanzan:

```text
DomainError
```

acompañado de un:

```text
ErrorCode
```

Ejemplo:

```python
raise DomainError(
    "La caja no esta abierta",
    ErrorCode.CASH_REGISTER_NOT_OPEN
)
```

Las respuestas HTTP se construyen mediante Exception Handlers globales.

Los Routers no deben envolver llamadas a Services en `try/except` únicamente para traducir `DomainError`.

---

## Eventos

Los eventos se generan desde los Services.

Nunca desde los Routers.

Esto garantiza que un evento represente una operación de negocio efectivamente realizada.

Ejemplo:

```text
Service
   ↓
modifica estado
   ↓
commit
   ↓
emite evento
```

Los eventos deben contener únicamente la información necesaria para que los clientes interesados puedan reaccionar.

---

## Validaciones

Las validaciones que protegen:

- integridad de datos;
- reglas de negocio;
- permisos;
- transiciones de estado;
- pertenencia a restaurante;

deben ejecutarse siempre en el backend.

Toda validación realizada en el frontend se considera una mejora de experiencia de usuario.

> El frontend puede anticipar una validación, pero nunca sustituirla.

---

## Multi-tenancy

Toda operación sobre datos pertenecientes a un restaurante debe estar acotada por `restaurant_id`.

Ejemplo:

```python
.filter(
    Product.id == product_id,
    Product.restaurant_id == restaurant_id
)
```

No debe aceptarse que un identificador enviado por el cliente determine por sí solo el acceso a una entidad.

Esta regla constituye una frontera de seguridad entre restaurantes.

---

## Migraciones

Toda modificación del esquema de base de datos debe realizarse mediante Alembic.

No se utiliza:

```python
Base.metadata.create_all()
```

para crear o evolucionar el esquema de producción.

Flujo habitual:

```text
modificación de Models
   ↓
alembic revision --autogenerate
   ↓
revisión manual de la migración
   ↓
alembic upgrade head
```

Las migraciones generadas automáticamente deben revisarse antes de incorporarse al repositorio.

---

## Excepción actual: autenticación

Actualmente el módulo `auth` puede acceder directamente a la base de datos desde el Router.

Esta excepción se acepta porque:

- implementa únicamente autenticación básica y consulta del usuario autenticado;
- la lógica actual es reducida;
- introducir un Service únicamente para delegar esas operaciones aportaría poco valor en este momento.

Esta excepción no debe utilizarse como precedente para otros módulos.

Si `auth` incorpora funcionalidades como:

- refresh tokens;
- revocación de tokens;
- recuperación de contraseña;
- MFA;
- sesiones persistentes;
- auditoría de accesos;

deberá evaluarse su migración al mismo patrón `Router → Service` utilizado por el resto del backend.

---

## Filosofía

> Los Routers deben ser aburridos.

Si un Router ocupa más de una pantalla, contiene consultas SQLAlchemy importantes o toma decisiones de negocio, probablemente exista lógica que debería trasladarse a un Service.

Se prioriza:

- claridad sobre abstracción innecesaria;
- consistencia sobre soluciones especiales;
- código explícito sobre comportamiento implícito;
- reglas de negocio centralizadas;
- tipos claros;
- errores previsibles;
- cambios pequeños y justificables.

El objetivo no es crear la mayor cantidad posible de capas o patrones.

El objetivo es que un programador pueda comprender dónde pertenece una nueva funcionalidad y modificarla sin introducir inconsistencias.