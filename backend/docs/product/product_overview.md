# Product Overview

## Introducción

Marcha es un sistema integral de gestión para restaurantes diseñado para operar dentro de la red local del establecimiento, con mínima dependencia de Internet.

El producto centraliza las principales tareas operativas de un restaurante:

- salón;
- pedidos;
- producción;
- caja;
- usuarios;
- administración;
- reportes;
- backups.

Marcha está pensado especialmente para establecimientos que necesitan una herramienta simple, confiable y disponible durante todo el turno de trabajo.

---

# Problema que resuelve

En muchos restaurantes la operación diaria depende de una combinación de:

- anotaciones manuales;
- comandas en papel;
- mensajes verbales;
- sistemas aislados;
- dispositivos no sincronizados;
- conexión a Internet;
- procesos de caja poco integrados.

Esto puede provocar:

```text
pedidos perdidos
errores de comunicación
duplicación de comandas
demoras
confusión en cocina
cobros incorrectos
dificultad para controlar caja
```

Marcha busca reducir esos problemas mediante una única plataforma operativa.

---

# Propuesta de valor

La propuesta principal de Marcha es:

> Centralizar el funcionamiento cotidiano del restaurante en un sistema local, simple y sincronizado.

Sus principales características diferenciales son:

- funcionamiento en red local;
- operación sin Internet permanente;
- acceso desde dispositivos comunes;
- sincronización en tiempo real;
- separación por roles;
- control de estados;
- gestión de caja integrada;
- backups incorporados;
- instalación administrada;
- licencia offline.

---

# Usuarios

Marcha contempla actualmente cuatro perfiles principales:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

---

## Administrator

Administra la configuración del establecimiento.

Puede gestionar:

- usuarios;
- productos;
- categorías;
- estaciones;
- mesas;
- layout;
- configuración;
- backups;
- reportes.

---

## Waiter

Gestiona la relación con el salón.

Puede:

- consultar mesas;
- abrir pedidos;
- agregar productos;
- modificar items pendientes;
- enviar pedidos;
- consultar estados;
- entregar productos.

---

## Kitchen

Gestiona la producción.

Puede:

- consultar items asignados;
- visualizar estaciones;
- iniciar preparación;
- marcar productos como listos.

---

## Cashier

Gestiona operaciones económicas.

Puede:

- abrir caja;
- registrar pagos;
- registrar movimientos;
- consultar estado de caja;
- cerrar órdenes;
- cerrar caja.

---

# Flujo principal

El flujo operativo típico es:

```text
Abrir caja
    ↓
Cliente ocupa mesa
    ↓
Mozo abre pedido
    ↓
Agrega productos
    ↓
Envía a producción
    ↓
Cocina prepara
    ↓
Producto READY
    ↓
Mozo entrega
    ↓
Caja cobra
    ↓
Orden CLOSED
    ↓
Cierre de caja
```

---

# Gestión de mesas

Marcha permite representar las mesas del restaurante mediante una interfaz gráfica.

Cada mesa puede contener información como:

- número;
- estado;
- posición;
- características visuales;
- pedido activo.

El objetivo es que el usuario pueda comprender rápidamente la situación del salón.

---

# Gestión de pedidos

Los pedidos contienen uno o más productos.

Cada pedido mantiene información sobre:

- mesa;
- estado;
- items;
- precios;
- descuentos;
- pagos;
- saldo.

El sistema controla las transiciones permitidas.

---

# Gestión de productos

Los productos pueden organizarse mediante:

```text
categorías
estaciones de producción
```

Cada producto contiene información como:

```text
nombre
precio
estado activo
categoría
estación
```

---

# Producción

Los productos pueden enviarse a distintas estaciones.

Ejemplo:

```text
Hamburguesa → Cocina
Refresco    → Barra
```

Esto permite distribuir automáticamente el trabajo.

---

# Estados de producción

Los items siguen un flujo controlado:

```text
PENDING
↓
SENT
↓
IN_PROGRESS
↓
READY
↓
DELIVERED
```

También pueden existir cancelaciones cuando corresponda.

---

# Tiempo real

Marcha mantiene sincronizados los distintos puestos mediante WebSockets.

Ejemplo:

```text
Cocina marca READY
        ↓
Mozo recibe actualización
        ↓
pedido destacado
        ↓
notificación sonora
```

---

# Caja

La caja integra:

- apertura;
- pagos;
- efectivo;
- tarjeta;
- transferencia;
- ingresos;
- egresos;
- total de ventas;
- efectivo esperado;
- efectivo contado;
- diferencia.

---

# Pagos

Una orden puede contener uno o varios pagos.

Métodos actuales:

```text
CASH
CARD
TRANSFER
```

El sistema controla que los pagos sean consistentes con el saldo pendiente.

---

# Reportes

Marcha puede ofrecer información sobre:

- ventas;
- productos;
- medios de pago;
- tickets;
- caja;
- períodos;
- comportamiento histórico.

Los reportes utilizan información almacenada por el propio sistema.

---

# Backups

Marcha incorpora backups:

```text
manuales
automáticos
diarios
semanales
mensuales
```

También dispone de:

- retención;
- restore;
- pre-restore;
- descarga;
- envío por email cuando está configurado.

---

# Operación offline

La operación principal funciona dentro de la LAN.

No necesita servicios cloud externos para:

```text
pedidos
cocina
caja
usuarios
productos
mesas
reportes locales
```

Esto reduce dependencia de conectividad.

---

# Dispositivos

El sistema puede utilizarse desde:

- PC;
- notebook;
- tablet;
- teléfono.

Solo se requiere un navegador moderno conectado a la red local.

---

# Servidor

Marcha se ejecuta sobre un servidor Linux.

La instalación productiva utiliza:

```text
Docker
Docker Compose
PostgreSQL
Redis
Nginx
systemd
```

---

# Instalación

El producto incluye procedimientos para:

```text
instalar
iniciar
detener
actualizar
desinstalar
```

El objetivo es reducir el trabajo técnico necesario en el restaurante.

---

# Licenciamiento

Marcha utiliza licencias offline vinculadas a la máquina.

No requiere conexión a un servidor externo de licencias.

---

# Público objetivo

Marcha está orientado principalmente a:

- restaurantes;
- bares;
- cafeterías;
- locales gastronómicos;
- establecimientos pequeños y medianos.

Especialmente aquellos que valoran:

- independencia de Internet;
- simplicidad;
- operación local;
- control directo sobre los datos.

---

# Posicionamiento

Marcha no pretende competir únicamente por cantidad de funcionalidades.

La prioridad es:

```text
simplicidad
confiabilidad
velocidad operativa
autonomía
```

Una funcionalidad adicional no tiene valor si vuelve más difícil utilizar el sistema durante un turno real.

---

# Estado actual

Marcha dispone de una versión funcional del flujo principal.

Se han probado procesos como:

- instalación;
- migraciones;
- autenticación;
- pedidos;
- cocina;
- caja;
- WebSockets;
- backups;
- actualización;
- desinstalación;
- reinstalación;
- licenciamiento.

La siguiente etapa se centra en validación mediante uso real.

---

# Visión

La visión de Marcha es convertirse en una plataforma de gestión gastronómica confiable, simple de desplegar y adaptable a establecimientos reales.

La evolución del producto debe mantenerse alineada con una pregunta:

> ¿Esto mejora realmente el trabajo durante un turno de restaurante?

Si la respuesta es no, probablemente no sea prioritario.