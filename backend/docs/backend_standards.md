# Backend Coding Standards

Proyecto: Restaurant POS
Lenguaje: Python 3.13
Framework: FastAPI
ORM: SQLAlchemy 2.x
Migraciones: Alembic

Este documento reúne las convenciones utilizadas en todo el backend.

---

# Arquitectura

Se utiliza una arquitectura por capas.

Router
↓
Service
↓
Model

Nunca se coloca lógica de negocio en los Routers.

---

# Routers

Cada router debe contener:

- docstring inicial
- APIRouter()
- endpoints documentados
- summary
- description
- response_model cuando corresponda
- status_code explícito

Ejemplo

```python
@router.get(
    "/",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías",
    description="Devuelve las categorías del restaurante."
)
```

---

# Comentarios

Cada endpoint lleva un encabezado:

```python
# ----------------------------------------------------------------------------------------------------
# Listar categorías
# ----------------------------------------------------------------------------------------------------
```

---

# Depends

Siempre se utiliza Dependency Injection.

Nunca se instancia un Service manualmente desde un Router.

Correcto:

```python
service: ProductService = Depends(get_product_service)
```

Incorrecto:

```python
service = ProductService(db)
```

---

# Response Models

Siempre que el endpoint devuelve un recurso conocido se utiliza response_model.

Ejemplos:

ProductResponse

CategoryResponse

OrderDetail

CashMovementOut

---

Puede omitirse únicamente cuando:

- devuelve un archivo
- devuelve StreamingResponse
- devuelve Response
- devuelve datos completamente dinámicos

---

# Status Codes

Siempre explícitos.

201

Creación.

200

Consulta o actualización.

204

Cuando realmente no existe cuerpo.

---

# HTTPException

Las validaciones de negocio deben vivir en los Services.

El Router únicamente lanza HTTPException cuando se trata de aspectos propios del protocolo HTTP.

---

# Schemas

Separar claramente:

Create

Update

Response

Summary

Detail

Nunca reutilizar un Create como Response.

Los schemas base (EntityBase) sólo se utilizarán cuando exista una cantidad significativa de campos compartidos entre múltiples schemas. Si únicamente comparten uno o dos atributos, se prefiere repetirlos para mantener los schemas simples y explícitos.

---

# Services

Todos los Services siguen la misma estructura.

1. __init__
2. Helpers privados (_...)
3. CRUD
4. Métodos especializados

Los Services:

- contienen toda la lógica de negocio;
- realizan las consultas SQLAlchemy;
- lanzan DomainError;
- nunca lanzan HTTPException;
- son los únicos responsables de hacer commit();
- nunca conocen detalles HTTP.

Los services deben devolver modelos SQLAlchemy o schemas tipados. Se evitará devolver diccionarios anónimos (dict) salvo en respuestas dinámicas (dashboards, reportes o agregaciones donde no exista un schema adecuado).


Los métodos siguen la nomenclatura:

- get_xxx()
- list_xxx()
- create_xxx()
- update_xxx()
- delete_xxx()
- toggle_xxx()

Los métodos privados comienzan por "_".

Las consultas SQLAlchemy se escriben siempre en formato multilínea para mantener legibilidad.

---

# Models

Representan exclusivamente las tablas.

No contienen reglas del negocio.

---

# Nombres

Routers

```
category.py
product.py
table.py
```

Services

```
product_service.py
table_service.py
```

Dependencies

```
dependencies.py
```

Schemas

```
ProductCreate
ProductUpdate
ProductResponse
ProductDetail
```

---

# Errores

Los Services lanzan DomainError.

Las respuestas HTTP son construidas por los Exception Handlers.

---

# Eventos

Los Services son responsables de emitir eventos.

Nunca los Routers.

---

# Filosofía

Los Routers deben ser aburridos.

Si un Router ocupa más de una pantalla o contiene decisiones de negocio, probablemente haya lógica que debería estar en un Service.

Toda validación realizada en el frontend se considera una mejora de experiencia de usuario. Las validaciones que garantizan la integridad de los datos y las reglas de negocio deben realizarse siempre en el backend, independientemente de que el frontend ya las implemente.

# Decisiones arquitectónicas

Esta sección documenta decisiones tomadas durante el desarrollo
y que no deben modificarse salvo una justificación clara.

Ejemplo:

2026-07

Se reemplazó create_all() por Alembic.

Motivo:

Los backups restaurados perdían los DEFAULT de las secuencias
porque las tablas originales habían sido creadas mediante
Base.metadata.create_all() y posteriormente migradas con Alembic.

A partir de esta fecha toda modificación del esquema se realiza
únicamente mediante Alembic.


Excepción: autenticación

El módulo auth es el único router que accede directamente a la base de datos.

Se considera aceptable porque:

implementa únicamente login y consulta del usuario autenticado,
la lógica es muy reducida y
evita agregar un servicio cuya única responsabilidad sería delegar llamadas.

Si en el futuro se agregan funcionalidades como refresh tokens, logout, revocación de tokens, recuperación de contraseña, MFA, etc., deberá migrarse al mismo patrón utilizado por el resto de los dominios (Router → Service → Repository).