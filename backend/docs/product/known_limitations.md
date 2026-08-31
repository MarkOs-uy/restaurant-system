# Known Limitations

## Objetivo

Este documento registra limitaciones conocidas de la versión actual de Marcha.

Una limitación conocida no implica necesariamente un defecto.

Puede representar:

- una decisión de alcance;
- una función todavía no implementada;
- una restricción técnica;
- una simplificación consciente.

Documentarlas evita que sean confundidas con errores o capacidades existentes.

---

# Operación local

Marcha está diseñado principalmente para operar dentro de la red local del restaurante.

Esto implica que el acceso remoto desde Internet no forma parte actualmente del flujo principal.

---

# Internet

Marcha puede operar sin Internet, pero ciertas funciones complementarias pueden dejar de estar disponibles.

Ejemplos:

```text
envío de email
actualizaciones
descarga de dependencias
servicios externos futuros
```

---

# mDNS

El acceso:

```text
http://pos.local
```

depende del soporte mDNS del dispositivo y de la red.

No todos los clientes resuelven `.local` de la misma forma.

La alternativa soportada es acceder mediante IP.

---

# Dispositivos cliente

El sistema utiliza navegador web.

No existe actualmente una app móvil nativa independiente.

---

# Hardware específico

No existe soporte universal para hardware especializado.

Ejemplos:

```text
impresoras fiscales
comanderas propietarias
lectores especializados
cajones de dinero
```

Las integraciones deben desarrollarse de forma explícita.

---

# Facturación electrónica

La facturación electrónica integrada no forma parte actualmente del núcleo documentado de Marcha.

---

# Delivery externo

No existe actualmente integración nativa documentada con plataformas externas de delivery.

---

# Reservas

La gestión de reservas no forma parte del flujo principal actual.

---

# Inventario avanzado

Marcha administra productos para venta.

No debe asumirse actualmente un módulo completo de:

```text
stock
recetas
ingredientes
mermas
costos de producción
compras
proveedores
```

salvo implementación futura.

---

# Contabilidad

Marcha no pretende reemplazar un sistema contable completo.

La gestión de caja y ventas es operativa.

No equivale a:

- contabilidad general;
- balances;
- impuestos;
- conciliación bancaria completa.

---

# RRHH

No existe actualmente un módulo completo de:

```text
horarios
sueldos
asistencia
recursos humanos
```

---

# Fidelización

No existe actualmente un sistema avanzado de:

```text
clientes
puntos
recompensas
CRM
marketing
```

---

# Multi-sucursal

El modelo soporta `restaurant_id`, pero esto no implica que la versión actual incluya todas las funciones necesarias para una administración centralizada de múltiples locales.

Ejemplos que podrían requerir desarrollo adicional:

```text
reportes consolidados
usuarios corporativos
configuración central
sincronización entre locales
```

---

# Cloud

Marcha no depende actualmente de una plataforma cloud central.

Esto es una ventaja operativa, pero también significa que determinadas funciones remotas no existen por defecto.

---

# Redis

Redis participa en la distribución de eventos.

Si existe una interrupción temporal:

- PostgreSQL conserva el estado;
- algunos eventos podrían no llegar al cliente;
- el cliente debe reconstruir estado mediante HTTP.

---

# WebSockets

Los WebSockets mejoran la sincronización, pero no constituyen un historial garantizado.

Una pérdida temporal de conexión puede provocar que el cliente no reciba un evento.

Por eso:

```text
HTTP
```

continúa siendo el mecanismo para recuperar el estado definitivo.

---

# SQLite en tests

Los unit tests actuales utilizan SQLite in-memory en determinadas áreas.

SQLite no reproduce completamente PostgreSQL.

Por ello todavía se necesitan tests de integración para:

```text
locking
native enums
constraints
dialect
concurrencia
```

---

# Cobertura de testing

La suite automatizada actual prioriza funcionalidades de alto riesgo.

No debe asumirse que todas las áreas del sistema cuentan con cobertura automática equivalente.

Las áreas P0 y P1 tienen prioridad sobre cobertura porcentual general.

---

# Frontend

El frontend depende de navegadores modernos.

Navegadores antiguos no forman parte del objetivo principal.

---

# Audio

Las notificaciones sonoras pueden estar limitadas por políticas del navegador.

Por ejemplo:

```text
autoplay bloqueado
```

El sistema debe continuar funcionando aunque el sonido no pueda reproducirse.

---

# Backup local

Un backup almacenado únicamente en el mismo servidor no protege contra:

```text
fallo físico total
robo
incendio
pérdida del disco
```

Debe mantenerse una estrategia de copia externa cuando el riesgo lo justifique.

---

# SMTP

El envío de backups por correo depende de:

- Internet;
- servidor SMTP;
- credenciales válidas.

El backup local continúa siendo independiente.

---

# Licencia

La licencia está vinculada a una identidad del host.

Cambios en:

```text
machine-id
product_uuid
```

pueden invalidar una licencia existente.

Un cambio completo de servidor normalmente requerirá emitir una nueva licencia.

---

# Protección anticopia

El licenciamiento dificulta la copia simple del producto.

No constituye protección absoluta frente a ingeniería inversa realizada por un atacante con suficiente acceso y conocimiento.

---

# Actualizaciones

Actualmente las actualizaciones requieren acceso técnico al servidor y disponibilidad del repositorio/origen correspondiente.

No existe necesariamente un sistema de actualización automática completamente desatendido.

---

# Rollback

El proceso dispone de backups pre-update, pero una reversión completa puede requerir coordinación entre:

```text
versión de código
versión de base
migraciones
```

No todo cambio puede revertirse simplemente mediante Git.

---

# Instalación

Aunque el proceso está automatizado, todavía existe una fase inicial que requiere:

- preparar servidor;
- obtener fingerprint;
- emitir licencia;
- copiar licencia;
- ejecutar instalador.

Una evolución futura puede simplificar aún más este procedimiento.

---

# Dependencia del servidor local

Si el servidor físico deja de funcionar:

> todo el restaurante pierde acceso al sistema hasta recuperar o sustituir el servidor.

Esto es inherente al modelo local centralizado.

La mitigación principal es:

```text
hardware confiable
backups
procedimiento de recuperación
```

---

# Alta disponibilidad

La versión actual no está diseñada como cluster de alta disponibilidad.

No incluye por defecto:

```text
PostgreSQL replication
failover automático
servidores redundantes
```

Para el mercado objetivo inicial, la prioridad es simplicidad operativa.

---

# Escala

La arquitectura actual está pensada para establecimientos pequeños y medianos.

Una operación de escala considerable podría requerir:

- benchmarking;
- tuning;
- infraestructura adicional;
- cambios de despliegue.

---

# Funcionalidades futuras

Una funcionalidad mencionada en:

```text
roadmap.md
```

no debe considerarse disponible hasta que:

- esté implementada;
- probada;
- documentada;
- incluida en una release.

---

# Limitaciones vs bugs

Debe distinguirse:

```text
BUG
→ algo que debería funcionar y no funciona

LIMITATION
→ algo que actualmente no se pretende soportar
```

Ejemplo:

```text
No hay reservas
→ limitation

Se pierde una orden activa
→ bug
```

---

# Pilotos

Durante los pilotos este archivo debe actualizarse con limitaciones reales detectadas.

Es preferible documentar claramente una restricción antes que ocultarla o permitir que cada cliente la descubra por accidente.

---

# Evolución

Una limitación puede convertirse en:

```text
feature
```

si aparece una necesidad comercial suficiente.

También puede permanecer deliberadamente fuera de alcance.

---

# Regla final

Este documento no debe utilizarse para justificar defectos.

Su función es establecer expectativas reales sobre el producto.

> Marcha debe prometer únicamente aquello que puede hacer de forma confiable.