# Troubleshooting

## Objetivo

Este documento contiene procedimientos de diagnóstico para problemas frecuentes de Marcha en producción.

La regla principal es:

> diagnosticar antes de destruir o reinstalar.

No debe utilizarse como primera respuesta:

```bash
docker compose down -v
```

porque puede eliminar la base de datos.

---

# 1. Marcha no abre en el navegador

Comprobar:

```bash
systemctl status pos-restaurant
```

Luego:

```bash
docker compose -f docker-compose.prod.yml ps
```

---

## Probar desde el servidor

```bash
curl http://localhost
```

Backend:

```bash
curl http://localhost/api/health
```

o la ruta correspondiente configurada por Nginx.

---

## Probar IP

Si:

```text
http://pos.local
```

no funciona, probar:

```text
http://<IP-servidor>
```

Si IP funciona pero `pos.local` no:

> el problema probablemente corresponde a mDNS / Avahi, no a Marcha.

---

# 2. pos.local no resuelve

Verificar:

```bash
systemctl status avahi-daemon
```

y:

```bash
systemctl status pos-zeroconf
```

Comprobar hostname.

Algunos dispositivos o redes no soportan correctamente mDNS.

Utilizar IP local como alternativa válida.

---

# 3. Backend no inicia

Verificar:

```bash
systemctl status pos-restaurant
```

Logs:

```bash
journalctl -u pos-restaurant -n 100
```

Docker:

```bash
docker compose -f docker-compose.prod.yml logs backend
```

---

# 4. Backend se reinicia continuamente

Comprobar:

```bash
docker compose -f docker-compose.prod.yml ps
```

Luego:

```bash
docker inspect <backend-container>
```

Revisar:

```text
State
RestartCount
ExitCode
```

Finalmente:

```bash
docker compose -f docker-compose.prod.yml logs --tail=200 backend
```

Causas posibles:

```text
licencia inválida
PostgreSQL no disponible
migración fallida
.env incorrecto
configuración faltante
error de código
```

---

# 5. Licencia no encontrada

Ruta esperada:

```text
/var/lib/pos-restaurant/license.json
```

Comprobar:

```bash
ls -l /var/lib/pos-restaurant/license.json
```

Debe ser un archivo regular.

No debe aparecer como:

```text
license.json/
```

---

# 6. license.json es un directorio

Esto puede ocurrir por un bind mount ejecutado cuando el archivo fuente no existía.

Comprobar:

```bash
file /var/lib/pos-restaurant/license.json
```

Si es directorio:

1. detener Marcha;
2. eliminar el directorio incorrecto;
3. copiar el archivo de licencia correcto;
4. iniciar nuevamente.

No generar una licencia nueva sin comprobar primero el fingerprint.

---

# 7. Licencia pertenece a otra máquina

Calcular nuevamente el fingerprint del host.

Compararlo con el utilizado al emitir la licencia.

Revisar:

```text
/etc/machine-id
/sys/class/dmi/id/product_uuid
```

Si cambió la identidad del host, será necesaria una nueva licencia.

---

# 8. PostgreSQL no inicia

Comprobar:

```bash
docker compose -f docker-compose.prod.yml ps
```

Logs:

```bash
docker compose -f docker-compose.prod.yml logs db
```

Revisar también espacio en disco:

```bash
df -h
```

---

# 9. Disco lleno

Docker puede consumir gran cantidad de espacio mediante:

```text
images
build cache
logs
volumes
```

Diagnóstico:

```bash
df -h
```

```bash
docker system df
```

No eliminar volúmenes indiscriminadamente.

Antes de limpiar:

> identificar exactamente qué ocupa espacio.

---

# 10. apt muestra errores extraños

Si aparecen errores de:

```text
GPG
temporary files
signature verification
```

comprobar primero:

```bash
df -h
```

Un filesystem casi lleno puede provocar errores aparentemente relacionados con paquetes o claves.

---

# 11. Alembic falla

Logs backend:

```bash
docker compose -f docker-compose.prod.yml logs backend
```

Comprobar revisión:

```bash
alembic current
```

```bash
alembic heads
```

No modificar manualmente la tabla:

```text
alembic_version
```

sin comprender el estado real del esquema.

---

# 12. Host "db" no se resuelve

Una URL como:

```text
postgresql://...@db:5432/...
```

funciona desde la red Docker.

Si Alembic se ejecuta directamente desde el host:

```text
db
```

no necesariamente existe en DNS.

Usar la dirección configurada para acceso desde el host, normalmente:

```text
localhost
```

con el puerto publicado correspondiente.

---

# 13. Frontend no muestra los últimos cambios

Comprobar si se realizó únicamente:

```bash
git pull
```

Eso no reconstruye el frontend productivo.

Debe ejecutarse el procedimiento de update o reconstruir explícitamente:

```bash
docker compose -f docker-compose.prod.yml up -d --build frontend
```

Después realizar:

```text
Ctrl + F5
```

en el navegador si existe cache.

---

# 14. Frontend build falla en Linux pero funciona en Windows

Revisar:

```text
mayúsculas/minúsculas
imports
exports
variables no utilizadas
tipos duplicados
```

Linux distingue:

```text
MyFile.ts
myFile.ts
```

Windows puede ocultar el problema durante desarrollo.

---

# 15. WebSockets no funcionan

Comprobar primero que HTTP normal funcione.

Luego revisar:

```text
/ws
```

en Nginx.

El frontend no debe depender de:

```text
localhost
```

o:

```text
pos.local
```

fijo.

Debe utilizar el host actual cuando corresponda.

---

# 16. Funciona en PC pero no en teléfono

Comprobar:

```text
misma red Wi-Fi/LAN
IP correcta
firewall
mDNS
WebSocket
```

Probar mediante IP:

```text
http://192.168.x.x
```

Si funciona con IP pero no con nombre:

```text
problema mDNS
```

---

# 17. Login falla

Comprobar:

- backend saludable;
- usuario existente;
- usuario activo;
- rol correcto;
- token;
- `restaurant_id`.

Logs backend pueden revelar:

```text
UNAUTHORIZED
usuario inexistente
token inválido
```

---

# 18. Usuario cambió de rol y dejó de funcionar

Marcha compara el rol presente en el token con el rol actual almacenado en base.

Si el rol cambió:

> el usuario debe iniciar sesión nuevamente.

Esto es comportamiento esperado.

---

# 19. Caja no abre

Comprobar si ya existe una caja abierta.

Error esperado:

```text
CASH_REGISTER_ALREADY_OPEN
```

Consultar el estado actual antes de modificar datos manualmente.

---

# 20. Caja no cierra

Puede existir:

```text
CASH_REGISTER_PENDING_ORDERS
```

Revisar órdenes activas.

No debe forzarse el cierre modificando directamente PostgreSQL salvo procedimiento excepcional documentado.

---

# 21. expected_cash parece incorrecto

Recordar:

```text
expected_cash =
opening_amount
+ CASH payments
+ cash_in
- cash_out
```

Los pagos:

```text
CARD
TRANSFER
```

suman ventas, pero no efectivo esperado.

---

# 22. Orden no cierra

Revisar:

```text
saldo pendiente
items no entregados
orden vacía
estado actual
```

Posibles errores:

```text
ORDER_HAS_REMAINING_BALANCE
ORDER_ITEMS_NOT_DELIVERED
ORDER_EMPTY
ORDER_ALREADY_CLOSED
```

---

# 23. Pago no puede registrarse

Comprobar:

```text
caja abierta
saldo restante
orden no cerrada
método de pago válido
```

Errores posibles:

```text
CASH_REGISTER_NOT_OPEN
PAYMENT_EXCEEDS_REMAINING
PAYMENT_INVALID_METHOD
```

---

# 24. Backup falla

Revisar:

```bash
docker compose -f docker-compose.prod.yml logs backend
```

Comprobar:

```text
BACKUP_DIR
permisos
espacio en disco
pg_dump
```

---

# 25. Backup intenta escribir en ubicación incorrecta

Comprobar:

```text
BACKUP_DIR
```

en la configuración.

En tests se utiliza `tmp_path`, pero producción debe utilizar el directorio configurado.

---

# 26. Restauración falla

No repetir la restauración ciegamente.

Comprobar:

```text
archivo válido
versión PostgreSQL
espacio libre
logs
permisos
```

Conservar:

```text
pre-restore backup
```

antes de intentar nuevas acciones.

---

# 27. SMTP no funciona

Comprobar:

```text
host
port
user
password
from
TLS/SSL
Internet
```

La falta de SMTP no debería impedir crear backups locales.

---

# 28. Contraseña SMTP dejó de descifrarse

Comprobar que:

```text
ENCRYPTION_KEY
```

sea la misma utilizada cuando se guardó la contraseña.

Si `.env` fue regenerado y cambió la clave, la contraseña cifrada anterior puede quedar ilegible.

---

# 29. Git dice repositorio sucio durante update

Ejecutar:

```bash
git status
```

Identificar archivos modificados.

Causas comunes:

```text
ediciones manuales
cambios de permisos
archivos productivos dentro del repo
```

La licencia no debe encontrarse dentro del repositorio.

---

# 30. Script no es ejecutable

Comprobar:

```bash
ls -l scripts/
```

Los permisos ejecutables deben estar versionados en Git.

Si un script nuevo no fue registrado correctamente:

```bash
git add --chmod=+x <script>
```

y luego commit.

---

# 31. Servicio systemd aparece failed

Comprobar:

```bash
systemctl status pos-restaurant
```

y:

```bash
journalctl -u pos-restaurant
```

Un estado `failed` puede ser correcto cuando el backend no logra superar su startup.

No debe ocultarse el error reiniciando continuamente sin investigar la causa.

---

# 32. Reiniciar Marcha

Procedimiento normal:

```bash
sudo ./start_server.sh
```

o mediante systemd según corresponda.

Para detener:

```bash
sudo ./stop_server.sh
```

---

# 33. Ver logs

Backend:

```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

PostgreSQL:

```bash
docker compose -f docker-compose.prod.yml logs -f db
```

Frontend:

```bash
docker compose -f docker-compose.prod.yml logs -f frontend
```

Redis:

```bash
docker compose -f docker-compose.prod.yml logs -f redis
```

---

# 34. Estado general

Los primeros comandos de diagnóstico deberían ser:

```bash
systemctl status pos-restaurant
```

```bash
docker compose -f docker-compose.prod.yml ps
```

```bash
df -h
```

```bash
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

Estos cuatro comandos resuelven o acotan una gran cantidad de problemas.

---

# 35. Acciones peligrosas

No ejecutar sin comprender las consecuencias:

```bash
docker compose down -v
```

```bash
docker volume rm ...
```

```bash
rm -rf /backups
```

```bash
rm -rf /var/lib/pos-restaurant
```

```sql
DROP DATABASE ...
```

---

# Escalamiento del diagnóstico

Orden recomendado:

```text
1. observar
2. leer logs
3. comprobar health
4. comprobar disco
5. comprobar configuración
6. comprobar Docker
7. comprobar base de datos
8. recién entonces modificar
```

---

# Información útil para reportar un problema

Al solicitar ayuda técnica incluir:

```text
qué operación se intentaba realizar
mensaje visible
hora aproximada
rol del usuario
endpoint o pantalla involucrada
systemctl status
docker compose ps
logs relevantes
```

No enviar:

```text
passwords
SECRET_KEY
ENCRYPTION_KEY
private license key
tokens completos
```

---

# Principio final

Cuando Marcha falla, evitar la tentación de:

```text
borrar
reinstalar
recrear todo
```

La persistencia es uno de los activos más importantes del sistema.

Primero:

```text
preservar datos
↓
diagnosticar
↓
identificar causa
↓
corregir
```

y solo después considerar acciones destructivas.