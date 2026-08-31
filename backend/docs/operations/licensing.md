# Licensing

## Objetivo

Este documento describe el sistema de licenciamiento offline utilizado por Marcha.

El objetivo es permitir instalaciones autorizadas sin requerir un servidor de licencias online.

---

# Principios

El sistema se basa en:

```text
licencia firmada digitalmente
+
fingerprint de máquina
+
verificación local
```

Marcha puede validar una licencia completamente offline.

---

# Componentes

Existen dos lados claramente separados.

## Emisión

Permanece bajo control del proveedor de Marcha.

Contiene:

```text
private key
herramientas de generación
```

## Verificación

Se distribuye con Marcha.

Contiene:

```text
public key
LicenseService
```

---

# Ed25519

Las licencias utilizan firmas digitales:

```text
Ed25519
```

La clave privada firma.

La clave pública verifica.

---

# Clave privada

La clave privada:

- nunca debe distribuirse;
- nunca debe incluirse en Docker;
- nunca debe guardarse en Git;
- nunca debe instalarse en el restaurante.

Se mantiene exclusivamente en el entorno privado utilizado para generar licencias.

---

# Clave pública

La clave pública puede distribuirse con el backend.

Ubicación conceptual:

```text
backend/app/infrastructure/licensing/public_key.pem
```

La clave pública permite verificar firmas.

No permite generar nuevas licencias válidas.

---

# Archivo de licencia

La licencia productiva se almacena en:

```text
/var/lib/pos-restaurant/license.json
```

El archivo permanece fuera del repositorio.

---

# Docker

El backend recibe la licencia mediante bind mount read-only.

Conceptualmente:

```text
/var/lib/pos-restaurant/license.json
        ↓
/license/license.json
```

---

# Precaución con bind mounts

Si Docker intenta montar un archivo inexistente en determinadas condiciones, puede crear un directorio con ese nombre.

Ejemplo problemático:

```text
license.json/
```

Por ello:

> la existencia de la licencia debe comprobarse antes de ejecutar Docker Compose.

`start_stack.sh` verifica que:

```bash
-f /var/lib/pos-restaurant/license.json
```

sea verdadero.

---

# Fingerprint

La licencia se vincula a una identidad calculada desde la máquina.

Actualmente se utilizan:

```text
/etc/machine-id
/sys/class/dmi/id/product_uuid
```

---

# Normalización

Los valores se normalizan antes de calcular el fingerprint.

Conceptualmente:

```text
machine-id
+
"|"
+
product_uuid
        ↓
lowercase
        ↓
SHA-256
```

Resultado:

```text
64 caracteres hexadecimales
```

---

# Fuente de identidad

El fingerprint se recalcula directamente desde el host.

No se utiliza como autoridad un archivo editable que contenga un identificador generado previamente.

---

# Docker y fingerprint

El contenedor backend recibe acceso read-only a:

```text
/etc/machine-id
/sys/class/dmi/id/product_uuid
```

del host.

El fingerprint calculado dentro del contenedor debe coincidir con el calculado durante instalación.

---

# Contenido de licencia

La licencia contiene información firmada.

Puede incluir conceptos como:

```text
product
customer
machine_id
expiry
```

La estructura exacta debe mantenerse compatible con el LicenseService.

---

# Canonicalización

Antes de firmar, el payload JSON se serializa de forma determinista.

Ejemplo conceptual:

```python
json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
)
```

La verificación debe utilizar exactamente la misma representación.

---

# Validaciones

El backend valida:

```text
producto
machine_id
fecha de expiración cuando existe
firma Ed25519
```

---

# Firma alterada

Si cualquier dato firmado cambia:

```text
customer
machine_id
expiry
product
```

la firma deja de ser válida.

El backend debe rechazar la licencia.

---

# Máquina incorrecta

Una licencia correctamente firmada para otra máquina también debe rechazarse.

Esto distingue:

```text
firma válida
```

de:

```text
licencia válida para este host
```

---

# Expiración

Cuando una licencia posee fecha de expiración, el backend debe comprobarla.

Las licencias sin expiración pueden mantenerse válidas indefinidamente mientras las demás condiciones sigan siendo correctas.

---

# Desarrollo

En:

```text
ENVIRONMENT=development
```

puede omitirse la validación de licencia.

Esto permite desarrollar sin una licencia productiva.

---

# Producción

En:

```text
ENVIRONMENT=production
```

la licencia es obligatoria.

No debe existir un fallback silencioso que permita iniciar sin licencia.

---

# Momento de validación

La licencia se valida antes de iniciar Uvicorn.

Flujo:

```text
PostgreSQL
↓
Alembic
↓
License validation
↓
Seed
↓
Uvicorn
```

Si la validación falla:

> el backend no inicia.

---

# Systemd

Dado que `start_stack.sh` espera `/health`, una licencia inválida provoca que:

```text
pos-restaurant.service
```

termine en estado fallido.

Esto evita falsos positivos de operación.

---

# Instalación sin licencia

`install.sh` debe detectar primero la ausencia de licencia.

Muestra el fingerprint y termina.

Después de generar y copiar la licencia:

```bash
sudo ./install.sh
```

puede ejecutarse nuevamente.

---

# Reinstalación

La licencia se conserva durante una desinstalación normal.

Esto permite:

```text
uninstall
↓
reinstall
```

sobre la misma máquina sin tener que emitir otra licencia.

---

# Cambio de máquina

Copiar:

```text
license.json
```

a otra máquina no debe funcionar.

El fingerprint será diferente.

Será necesaria una licencia emitida para la nueva máquina.

---

# Cambio de hardware

Cambios que alteren:

```text
machine-id
product_uuid
```

pueden modificar el fingerprint.

En ese caso la licencia actual puede dejar de ser válida.

---

# Seguridad del sistema

El licenciamiento dificulta copias simples de una instalación.

No debe considerarse un mecanismo absoluto contra ingeniería inversa.

El objetivo es:

```text
control comercial razonable
+
funcionamiento offline
+
simplicidad operativa
```

---

# Información que nunca debe publicarse

Nunca documentar ni distribuir:

```text
private key
seed privado
contraseñas
procedimientos inseguros de bypass productivo
```

Este documento describe la arquitectura, no secretos criptográficos.

---

# Tests mínimos

El sistema debe probar:

```text
licencia correcta → inicia
licencia modificada → falla
licencia de otra máquina → falla
licencia ausente → falla
```

---

# Regla final

La arquitectura debe mantener siempre esta separación:

```text
EMISIÓN
private key
fuera de Marcha

VERIFICACIÓN
public key
dentro de Marcha
```

Si una instalación distribuida puede emitir por sí misma una nueva licencia válida, la arquitectura está comprometida.