# Backend Structure

## Objetivo

El backend está organizado siguiendo una arquitectura por capas cuyo objetivo es:

- separar responsabilidades;
- mantener el código fácil de mantener;
- facilitar el testing;
- evitar lógica de negocio dentro de los routers;
- permitir reutilizar servicios desde distintos endpoints.

---

# Estructura

app/
├── api/
│   └── routers/
│
├── core/
│
├── db/
│
├── dependencies/
│
├── domain/
│
├── models/
│
├── schemas/
│
└── services externos (events, websocket, etc.)

---

## Routers

Los routers representan únicamente la capa HTTP.

Responsabilidades:

- definir endpoints;
- validar permisos mediante Depends();
- recibir parámetros;
- invocar el Service correspondiente;
- devolver el resultado.

Un router nunca debe contener lógica de negocio.

Ejemplo:

Cliente
↓
Router
↓
Service
↓
Repository/SQLAlchemy
↓
Base de datos

---

## Domain

Cada módulo del dominio contiene la lógica de negocio.

Ejemplo:

domain/
    product/
        dependencies.py
        product_service.py

El Service conoce las reglas del negocio.

Ejemplos:

- no permitir productos duplicados;
- validar estados;
- calcular descuentos;
- emitir eventos;
- actualizar varias tablas dentro de una transacción.

---

## Dependencies

Cada dominio expone una función get_xxx_service().

Ejemplo

```python
def get_product_service(
    db: Session = Depends(get_db)
):
    return ProductService(db)
```

FastAPI resuelve automáticamente las dependencias.

---

## Models

Representan exactamente las tablas de la base de datos.

No contienen lógica de negocio.

Se utilizan únicamente para persistencia mediante SQLAlchemy.

---

## Schemas

Los Schemas representan los datos que entran y salen de la API.

Nunca tienen por qué coincidir exactamente con los Models.

Es habitual tener:

- Create
- Update
- Response
- Detail
- Summary

Un Schema puede incluir campos calculados que no existen en la base de datos.

Ejemplo:

subtotal
total
remaining

---

## Services

Toda la lógica importante vive aquí.

Los Services pueden:

- consultar modelos
- actualizar varias entidades
- emitir eventos
- lanzar DomainErrors
- reutilizar otros Services

Los routers nunca deberían conocer esos detalles.

---

## Dependencias (flujo completo)

Cliente HTTP

↓

Router

↓

Depends(get_product_service)

↓

Depends(get_db)

↓

ProductService(db)

↓

SQLAlchemy

↓

PostgreSQL

---

## Eventos

Los eventos (WebSockets, Redis, etc.) se generan desde los Services.

Nunca desde los Routers.

De esta forma cualquier cliente (Waiter, Kitchen, Cashier, Admin) recibe las actualizaciones automáticamente.

---

## Principio general

El Router responde a la pregunta:

"¿Qué quiere hacer el usuario?"

El Service responde:

"¿Cómo debe hacerse correctamente?"