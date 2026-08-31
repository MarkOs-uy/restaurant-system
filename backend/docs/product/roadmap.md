# Roadmap

## Objetivo

Este documento describe la evolución prevista de Marcha.

El roadmap no constituye una promesa contractual de fechas o funcionalidades.

Su función es orientar decisiones de desarrollo según:

- riesgo;
- valor;
- feedback;
- pilotos;
- necesidades comerciales.

---

# Principio

La evolución de Marcha debe estar guiada por uso real.

La prioridad no es:

```text
agregar muchas funcionalidades
```

sino:

```text
convertir el producto actual en una herramienta confiable y vendible
```

---

# Etapa 1 — Estabilización técnica

Estado:

```text
muy avanzada
```

Objetivos:

- arquitectura backend;
- frontend funcional;
- PostgreSQL;
- Alembic;
- WebSockets;
- Redis;
- caja;
- pedidos;
- backups;
- instalación;
- actualización;
- licensing;
- documentación.

---

# Etapa 2 — Validación mediante piloto

Prioridad actual.

Objetivo:

> utilizar Marcha en restaurantes reales durante turnos reales.

---

## Preparación

Antes del piloto:

```text
datos reales
productos reales
mesas reales
usuarios reales
estaciones reales
dispositivos reales
Wi-Fi real
```

---

## Fase de prueba controlada

Ejecutar inicialmente escenarios ficticios.

Ejemplo:

```text
abrir caja
crear varias mesas
enviar pedidos
producir
entregar
cobrar
cerrar
```

---

## Uso real

Después:

```text
turnos completos
```

con supervisión mínima.

---

## Registro de hallazgos

Clasificar:

```text
BUG
FRICTION
MISSING
```

---

## BUG

Comportamiento incorrecto.

Prioridad alta.

Siempre que sea posible:

```text
test que reproduce
↓
fix
↓
regresión protegida
```

---

## FRICTION

La función existe pero molesta o enlentece el trabajo.

Ejemplo:

```text
demasiados clics
botón poco claro
feedback insuficiente
```

---

## MISSING

Capacidad requerida que todavía no existe.

No toda solicitud debe convertirse automáticamente en feature.

Debe verificarse:

```text
frecuencia
valor
impacto
complejidad
```

---

# Etapa 3 — Marcha 1.0

La versión 1.0 debería definirse después de validar el producto en operación real.

Criterio aproximado:

```text
flujo crítico estable
bugs P0 cerrados
bugs P1 principales cerrados
instalación reproducible
actualización segura
backup/restore probado
documentación básica completa
piloto satisfactorio
```

---

# Criterio operativo de 1.0

Un restaurante debería poder completar:

```text
abrir caja
↓
trabajar todo el turno
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

sin requerir intervención técnica.

---

# Etapa 4 — Mejoras derivadas del mercado

Después de 1.0, priorizar solicitudes repetidas por clientes.

Ejemplos posibles:

```text
reportes adicionales
mejoras de UX
impresión
nuevas formas de pago
gestión avanzada de productos
configuración más flexible
```

---

# Etapa 5 — Integraciones

Solo cuando exista demanda concreta.

Posibles áreas:

```text
facturación electrónica
delivery
reservas
proveedores
servicios externos
impresoras
contabilidad
```

---

# Etapa 6 — Multi-sucursal

El modelo actual ya utiliza:

```text
restaurant_id
```

Esto facilita una posible evolución hacia:

- múltiples locales;
- reportes consolidados;
- administración central.

No debe desarrollarse anticipadamente sin necesidad comercial.

---

# Etapa 7 — Servicios remotos opcionales

Una evolución futura podría incorporar componentes cloud opcionales.

Ejemplos:

```text
backup remoto
monitoreo
actualizaciones
panel central
métricas
soporte
```

El principio debería mantenerse:

> una caída de Internet no debe impedir operar el restaurante.

---

# Testing roadmap

Evolución recomendada:

```text
unit tests P0
↓
unit tests P1
↓
integration PostgreSQL
↓
API tests
↓
WebSocket tests
↓
E2E crítico
```

---

# Observabilidad

Posibles mejoras:

- logs estructurados;
- diagnóstico;
- métricas;
- reporte de errores;
- health checks ampliados.

---

# UX

Durante pilotos debe revisarse especialmente:

```text
cantidad de clics
tamaño de controles
legibilidad
velocidad
feedback
uso táctil
```

---

# Despliegue

Posibles evoluciones:

```text
instalador más amigable
diagnóstico automático
versionado de releases
rollback asistido
```

---

# Producto comercial

Además del software deberán evolucionar:

- documentación;
- soporte;
- instalación;
- licencias;
- precios;
- onboarding;
- mantenimiento;
- contrato;
- demos.

---

# Priorización

Toda propuesta debería evaluarse mediante:

```text
valor para cliente
frecuencia de necesidad
riesgo
costo
mantenimiento
impacto arquitectónico
```

---

# Matriz simple

```text
alto valor + bajo costo
→ hacer pronto

alto valor + alto costo
→ planificar

bajo valor + bajo costo
→ evaluar

bajo valor + alto costo
→ evitar
```

---

# Anti-roadmap

No se incorporará una funcionalidad únicamente porque:

- otro sistema la tenga;
- sea técnicamente interesante;
- esté de moda;
- pueda agregarse.

La existencia de una posibilidad técnica no constituye una necesidad de producto.

---

# Próximo objetivo

La prioridad inmediata es:

> validar Marcha durante operación real.

Los resultados del piloto determinarán el roadmap posterior con más precisión que cualquier planificación teórica.

---

# Regla final

El roadmap debe poder cambiar.

Lo que no debe cambiar fácilmente es el principio:

> Marcha debe resolver mejor el trabajo real del restaurante con la menor complejidad razonable.