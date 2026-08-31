# Update

## Objetivo

Este documento describe el procedimiento seguro para actualizar una instalación productiva de Marcha.

La actualización debe preservar:

```text
datos
configuración
licencia
backups
```

---

# Script

Las actualizaciones se realizan mediante:

```text
update.sh
```

No se recomienda actualizar una instalación productiva ejecutando manualmente una secuencia incompleta de comandos Git y Docker.

---

# Principio principal

Antes de modificar una instalación:

> crear primero un backup recuperable.

---

# Repositorio limpio

Antes de actualizar, el script verifica que el repositorio no contenga modificaciones locales inesperadas.

Ejemplo:

```bash
git status
```

Si existen cambios locales, la actualización debe detenerse.

Esto evita que:

```text
git pull
```

mezcle código productivo con modificaciones manuales no registradas.

---

# Archivos productivos fuera del repositorio

No deben generar cambios Git:

```text
license.json
.env
backups
```

La licencia productiva se encuentra en:

```text
/var/lib/pos-restaurant/license.json
```

y no dentro del repositorio.

---

# Backup pre-update

Antes de descargar código nuevo se genera un backup manual.

Ubicación conceptual:

```text
backups/manual-updates/
```

El backup se realiza antes de cualquier cambio importante.

Si el backup falla:

> la actualización debe abortarse.

---

# Retención

Los backups pre-update utilizan una retención limitada.

Actualmente el procedimiento conserva una cantidad acotada de backups recientes.

El objetivo es evitar crecimiento indefinido del disco.

---

# Flujo de actualización

```text
verificar Git
       ↓
backup pre-update
       ↓
git fetch
       ↓
git pull --ff-only
       ↓
detener servicio
       ↓
Docker build
       ↓
iniciar servicio
       ↓
Alembic desde backend
       ↓
health check
```

---

# Fast-forward only

El pull productivo utiliza:

```bash
git pull --ff-only
```

Esto evita crear merges automáticos inesperados en el servidor.

Si Git no puede realizar un fast-forward:

> la actualización debe detenerse para revisión manual.

---

# Alembic

`update.sh` no debe mantener una segunda implementación independiente de migraciones.

El backend ejecuta:

```text
alembic upgrade head
```

durante el startup.

Esto mantiene una única responsabilidad.

---

# Rebuild Docker

Los cambios de código no afectan contenedores ya construidos.

Por ello la actualización debe reconstruir imágenes cuando corresponda.

Especialmente:

```text
frontend
backend
```

---

# Frontend

Un simple:

```bash
git pull
```

no actualiza el frontend servido por Nginx.

Se necesita:

```text
Docker build
```

para generar un nuevo:

```text
dist/
```

dentro de la imagen productiva.

---

# Startup

Después del build:

```text
pos-restaurant.service
```

inicia el stack mediante:

```text
start_stack.sh
```

El servicio solo debe considerarse operativo después de superar:

```text
/health
```

---

# Fallo de actualización

Si el backend no puede iniciar después del update:

1. revisar logs;
2. identificar si el problema corresponde a:
   - código;
   - migración;
   - configuración;
   - licencia;
   - base de datos;
3. conservar el backup pre-update;
4. no destruir volúmenes.

---

# Rollback

Actualmente el mecanismo seguro de recuperación se basa en:

```text
código anterior
+
backup pre-update
```

Una reversión de código puede requerir también una estrategia compatible de migración.

No debe asumirse que:

```bash
git checkout <versión-anterior>
```

es suficiente si el esquema de base de datos ya fue modificado.

---

# Migraciones destructivas

Toda migración que:

- elimine columnas;
- transforme datos;
- elimine enums;
- modifique constraints críticas;

debe tratarse con especial precaución.

Debe existir un backup antes de aplicarla.

---

# Verificación posterior

Después de actualizar:

```bash
systemctl status pos-restaurant
```

```bash
docker compose -f docker-compose.prod.yml ps
```

Comprobar:

```text
login
mesas
órdenes
cocina
caja
WebSockets
```

---

# Checklist

```text
[ ] Git limpio
[ ] backup pre-update creado
[ ] pull --ff-only correcto
[ ] Docker build correcto
[ ] backend saludable
[ ] migraciones aplicadas
[ ] frontend accesible
[ ] login correcto
[ ] datos preservados
```

---

# Regla final

Una actualización no está terminada cuando:

```text
git pull
```

termina.

Está terminada cuando:

```text
el sistema vuelve a operar correctamente
+
los datos permanecen intactos
+
el backend está saludable
```