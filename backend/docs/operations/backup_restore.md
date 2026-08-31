# Backup and Restore

## Objetivo

Este documento describe la estrategia de backup y restauración de Marcha.

El objetivo es proteger los datos operativos del restaurante frente a:

- errores humanos;
- fallos de hardware;
- actualizaciones defectuosas;
- corrupción de datos;
- problemas de infraestructura.

---

# Principio fundamental

> Un backup no está realmente validado hasta que puede restaurarse.

Generar archivos de backup sin probar restauración no constituye una estrategia completa.

---

# Datos protegidos

La información principal se encuentra en PostgreSQL.

Incluye, entre otros:

```text
usuarios
productos
mesas
órdenes
items
pagos
cajas
movimientos
configuración
reportes derivados
```

---

# Sistema de backups

Marcha administra internamente sus backups.

Tipos soportados:

```text
manual
daily
weekly
monthly
pre-restore
manual-update
```

---

# Directorio

Los backups se almacenan fuera del volumen PostgreSQL.

Conceptualmente:

```text
/backups
```

desde el backend, con persistencia en el host mediante bind mount.

Esto permite conservar los archivos incluso si PostgreSQL debe ser reconstruido.

---

# Separación por restaurante

Los backups pueden organizarse por:

```text
restaurant_<id>
```

Ejemplo:

```text
backups/
└── restaurant_1/
    ├── daily/
    ├── weekly/
    ├── monthly/
    └── manual/
```

---

# Backup manual

Puede iniciarse desde las funciones administrativas de Marcha.

Debe utilizarse antes de operaciones particularmente sensibles cuando sea necesario.

---

# Backups automáticos

El sistema soporta frecuencias:

```text
DAILY
WEEKLY
MONTHLY
```

Cada restaurante puede disponer de configuración relacionada con:

```text
backup_frequency
backup_time
backup_weekday
backup_monthday
backup_timezone
```

---

# Zona horaria

La programación debe respetar la zona horaria configurada.

Ejemplo:

```text
America/Montevideo
```

Esto evita interpretar horarios de backup según UTC cuando el usuario espera hora local.

---

# Backup mensual

Si se configura un día que no existe en determinado mes:

```text
31 de febrero
```

el sistema debe utilizar un día válido equivalente, normalmente el último día disponible del mes.

---

# Retención

Marcha dispone de políticas de retención.

Ejemplos:

```text
backup_retention_daily
backup_retention_weekly
backup_retention_monthly
```

Los backups que superen el período configurado pueden eliminarse automáticamente.

---

# Retención cero

La convención vigente es:

```text
0
```

o ausencia equivalente:

```text
conservar indefinidamente
```

No debe interpretarse como:

```text
eliminar inmediatamente
```

---

# PostgreSQL dump

El backup de PostgreSQL utiliza las herramientas estándar correspondientes.

Conceptualmente:

```text
pg_dump
```

La ejecución debe comprobar el código de retorno.

Si falla:

```text
returncode != 0
```

la operación debe considerarse fallida.

No debe marcarse un backup como correcto si el dump no terminó correctamente.

---

# Errores

Los errores se convierten en errores controlados del dominio cuando corresponde.

El fallo debe quedar registrado y ser visible al administrador.

---

# Backup antes de restore

Antes de una restauración debe generarse, cuando corresponda, un:

```text
pre-restore backup
```

del estado actual.

Esto proporciona una última posibilidad de recuperación si el usuario restaura el archivo equivocado.

---

# Restauración

El proceso conceptual es:

```text
seleccionar backup
       ↓
validar archivo
       ↓
crear pre-restore
       ↓
preparar restauración
       ↓
detener operaciones necesarias
       ↓
restaurar PostgreSQL
       ↓
reiniciar backend
       ↓
verificar health
```

---

# Restauración y backend

La restauración puede requerir ejecutarse en un momento controlado del startup.

El backend puede detectar una restauración pendiente antes de continuar con:

```text
Alembic
licencia
seed
Uvicorn
```

Esto evita operar sobre una base parcialmente restaurada.

---

# Compatibilidad de versión

Debe considerarse la relación entre:

```text
versión del backup
versión del código
migraciones Alembic
```

Después de una restauración, el backend puede aplicar migraciones necesarias para llevar la base restaurada al esquema actual.

---

# Nunca restaurar sobre una base sin respaldo previo

Excepto cuando la base actual ya se considera descartable, debe existir una copia previa antes de reemplazarla.

---

# Descarga de backups

Los backups pueden descargarse desde el sistema cuando corresponda.

Esto permite conservar copias externas al servidor.

---

# Copia externa

Para mayor seguridad, al menos algunos backups deberían existir fuera del equipo servidor.

Posibles destinos:

```text
otro equipo
disco externo
almacenamiento remoto
correo electrónico
```

La disponibilidad de estos mecanismos puede depender de conectividad.

---

# Email

Marcha puede enviar backups mediante SMTP.

La falta de Internet o SMTP no debe afectar la creación del backup local.

---

# Credenciales SMTP

La contraseña SMTP se almacena cifrada.

Utiliza:

```text
ENCRYPTION_KEY
```

La pérdida de esa clave puede impedir recuperar la contraseña almacenada.

---

# Backup pre-update

`update.sh` crea un backup antes de actualizar el software.

Ubicación conceptual:

```text
backups/manual-updates/
```

Si ese backup falla:

> la actualización debe detenerse.

---

# Restauración de prueba

Periódicamente debe verificarse el procedimiento completo:

```text
crear datos conocidos
↓
backup
↓
modificar datos
↓
restore
↓
comprobar datos originales
```

---

# Qué no protege un backup de PostgreSQL

Un dump de base de datos no sustituye necesariamente la copia de:

```text
backend/.env
license.json
configuración del host
```

Estos elementos también deben considerarse en una recuperación completa del servidor.

---

# Elementos críticos de recuperación

Para reconstruir una instalación completa pueden ser necesarios:

```text
código Marcha
backup PostgreSQL
backend/.env
license.json
```

---

# Pérdida total del servidor

Ante fallo físico del servidor:

1. preparar nuevo servidor;
2. instalar Marcha;
3. generar una nueva licencia si el fingerprint cambia;
4. recuperar configuración;
5. restaurar backup PostgreSQL;
6. aplicar migraciones;
7. verificar el sistema.

Una licencia vinculada a la máquina anterior no debe asumirse válida para hardware nuevo.

---

# Checklist

```text
[ ] backup generado
[ ] archivo existe
[ ] tamaño razonable
[ ] pg_dump terminó correctamente
[ ] retención aplicada
[ ] copia externa disponible cuando corresponda
[ ] restauración probada periódicamente
```

---

# Regla final

La estrategia debe garantizar que ante un problema serio sea posible responder:

> ¿Cuál es el último punto conocido al que podemos volver y cómo lo restauramos?

Si esa respuesta no es clara, el sistema todavía no está suficientemente protegido.