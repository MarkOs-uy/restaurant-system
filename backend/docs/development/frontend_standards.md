# Frontend Coding Standards

Proyecto: Marcha  
Lenguaje: TypeScript  
Framework: React  
Build Tool: Vite

Este documento define las convenciones de desarrollo utilizadas en el frontend de Marcha.

Su objetivo es mantener un código:

- consistente;
- legible;
- fácil de mantener;
- predecible;
- tipado;
- reutilizable;
- alineado con la arquitectura general del sistema.

---

## Principio general

El frontend es responsable de:

- presentar información;
- capturar acciones del usuario;
- realizar validaciones de experiencia de usuario;
- comunicarse con el backend;
- mantener sincronizada la interfaz;
- reaccionar a eventos en tiempo real.

El frontend **no es la autoridad de las reglas de negocio**.

> Toda regla que garantice integridad, permisos o consistencia debe validarse nuevamente en el backend.

---

## Estructura general

La estructura puede evolucionar, pero debe conservar una separación clara de responsabilidades.

Ejemplo:

```text
src/
├── api/
├── assets/
│   ├── images/
│   └── sounds/
├── components/
├── pages/
├── types/
├── utils/
├── hooks/
├── context/
├── App.tsx
└── main.tsx
```

No todas las carpetas son obligatorias.

Deben introducirse únicamente cuando exista una responsabilidad clara que justifique su existencia.

---

## Pages

Las páginas representan vistas principales asociadas a rutas o áreas funcionales.

Ejemplos:

```text
LoginPage
TablesPage
OrderDetailPage
KitchenPage
CashierPage
ProductsPage
BackupsPage
ReportsPage
```

Una Page puede:

- cargar datos;
- mantener estado asociado a la pantalla;
- coordinar componentes;
- reaccionar a eventos WebSocket;
- realizar navegación;
- invocar funciones de API.

Debe evitar:

- duplicar lógica de API;
- contener funciones genéricas reutilizables;
- implementar reglas de negocio que correspondan al backend;
- crecer indefinidamente cuando existen partes claramente separables.

---

## Components

Los Components representan unidades visuales reutilizables o partes claramente identificables de una pantalla.

Ejemplo:

```text
ProductCard
DateRange
OrderItemRow
ProtectedRoute
StatusBadge
```

Un Component debería tener una responsabilidad visual concreta.

Cuando un bloque de una Page:

- se repite;
- tiene estado propio;
- posee lógica visual independiente;
- dificulta la lectura de la Page;

debe evaluarse convertirlo en un Component.

> No se extraen Components únicamente para reducir líneas de código.

La extracción debe mejorar legibilidad, reutilización o aislamiento de responsabilidades.

---

## TypeScript

Se utiliza TypeScript para todo el código nuevo del frontend.

Debe evitarse:

```typescript
any
```

salvo que exista una justificación concreta.

Se prefieren tipos explícitos:

```typescript
type Order = {
  id: number
  status: OrderStatus
}
```

frente a estructuras no tipadas.

Cuando un valor provenga de una fuente externa y su tipo no sea conocido, se prefiere:

```typescript
unknown
```

y luego realizar validación o narrowing.

Ejemplo:

```typescript
const context =
  rawContext &&
  typeof rawContext === "object" &&
  !Array.isArray(rawContext)
    ? rawContext as Record<string, unknown>
    : undefined
```

---

## Types

Los tipos compartidos deben ubicarse en:

```text
src/types/
```

cuando son utilizados por múltiples módulos.

Ejemplo:

```text
orderStatus.ts
paymentMethod.ts
userRole.ts
webSocketEvents.ts
```

Los tipos que pertenecen exclusivamente a un Component o Page pueden permanecer junto a ese módulo.

No debe centralizarse todo automáticamente en `types/`.

---

## Barrel exports

Cuando se utilice un archivo:

```text
types/index.ts
```

debe exportar únicamente tipos cuyo uso compartido esté claramente establecido.

Ejemplo:

```typescript
export * from "./orderStatus"
export * from "./paymentMethod"
export * from "./userRole"
export * from "./webSocketEvents"
```

Debe evitarse exportar dos tipos con el mismo nombre desde distintos módulos.

Los nombres de archivo e imports deben respetar exactamente mayúsculas y minúsculas.

Ejemplo correcto:

```typescript
import type { WebSocketEvent } from "../types/webSocketEvents"
```

Esto es especialmente importante porque Linux distingue mayúsculas y minúsculas aunque Windows pueda tolerarlas.

---

## API

Toda comunicación HTTP con el backend debe centralizarse mediante la utilidad común de API.

Ejemplo:

```typescript
apiFetch(...)
```

No deben utilizarse llamadas directas a `fetch()` dentro de Pages o Components salvo una necesidad excepcional y documentada.

Ejemplo:

```typescript
const data = await apiFetch("/products/")
```

Esto permite centralizar:

- autenticación;
- headers;
- serialización JSON;
- manejo de errores;
- respuestas `401`;
- comportamiento común.

---

## URLs de API

Las Pages y Components no deben construir URLs absolutas dependientes del servidor.

Debe utilizarse el mecanismo común definido por la aplicación.

En producción, la comunicación HTTP utiliza:

```text
/api
```

a través de Nginx.

Esto permite que el frontend funcione independientemente de la IP concreta del servidor.

---

## Manejo de errores

Los errores provenientes del backend deben procesarse mediante la utilidad común:

```typescript
handleApiError(error)
```

y no mediante `alert()` o mensajes improvisados distribuidos por la aplicación.

El backend puede devolver:

```text
error
detail
context
```

El frontend debe utilizar códigos de error estables para traducirlos a mensajes comprensibles para el usuario.

Ejemplo conceptual:

```typescript
switch (error.code) {
  case "CASH_REGISTER_NOT_OPEN":
    return "Debe abrir la caja antes de continuar."
}
```

> El mensaje técnico del backend no debe asumirse automáticamente como mensaje final para el usuario.

---

## Toasts

Los mensajes de error o confirmación no bloqueantes deben mostrarse mediante el sistema común de toast.

Ejemplo:

```typescript
showToast("Layout guardado")
```

No se utilizan:

```typescript
alert(...)
```

salvo una excepción explícita.

Los mensajes deben ser:

- breves;
- claros;
- orientados al usuario;
- libres de información técnica innecesaria.

---

## Estados de carga

Toda operación que pueda tardar perceptiblemente debe proporcionar feedback visual.

Ejemplo:

```typescript
const [loggingIn, setLoggingIn] = useState(false)
```

Y:

```tsx
<button disabled={loggingIn}>
  {loggingIn ? "Ingresando..." : "Ingresar"}
</button>
```

Debe evitarse permitir múltiples envíos accidentales mientras una operación está en curso.

---

## Formularios

Los formularios deben:

- utilizar componentes controlados cuando corresponda;
- prevenir envíos múltiples;
- proporcionar feedback al usuario;
- utilizar `autoComplete` apropiadamente;
- mantener validaciones simples de experiencia de usuario.

Ejemplo:

```tsx
<input
  type="text"
  autoComplete="username"
  value={username}
  onChange={event => setUsername(event.target.value)}
/>
```

La validación frontend no sustituye la validación del backend.

---

## Estado

Se utiliza estado local mediante React cuando el dato pertenece a una Page o Component específico.

Ejemplo:

```typescript
const [products, setProducts] = useState<Product[]>([])
```

No debe introducirse estado global únicamente para evitar pasar una prop ocasional.

El estado global debe reservarse para información realmente transversal.

Ejemplos posibles:

- autenticación;
- usuario actual;
- configuración global;
- estado compartido entre áreas independientes.

---

## useEffect

`useEffect` debe utilizarse para sincronizar el componente con sistemas externos o ciclos de vida.

Ejemplos válidos:

- cargar información inicial;
- registrar WebSockets;
- timers;
- event listeners;
- sincronización con APIs externas.

Debe evitarse utilizar `useEffect` para derivar valores que pueden calcularse directamente durante el render.

Incorrecto conceptualmente:

```typescript
useEffect(() => {
  setTotal(price * quantity)
}, [price, quantity])
```

Preferible:

```typescript
const total = price * quantity
```

---

## Limpieza de efectos

Todo `useEffect` que registre recursos debe liberar dichos recursos.

Ejemplo:

```typescript
useEffect(() => {
  const socket = new WebSocket(url)

  return () => {
    socket.close()
  }
}, [])
```

Esto aplica también a:

- timers;
- event listeners;
- subscriptions;
- observers.

---

## WebSockets

Los WebSockets se utilizan para mantener sincronizados los clientes en tiempo real.

Los componentes deben reaccionar únicamente a eventos relevantes para su pantalla.

Ejemplo:

```text
ORDER_UPDATED
ITEM_STATUS_CHANGED
ITEM_READY
CASH_REGISTER_UPDATED
```

Un evento WebSocket debe considerarse principalmente una señal de que ocurrió un cambio.

Cuando sea más seguro o sencillo, el cliente puede volver a consultar el recurso mediante HTTP.

> WebSocket notifica. HTTP confirma el estado actual.

Esto reduce inconsistencias derivadas de intentar reconstruir todo el estado únicamente mediante eventos.

---

## Conexiones WebSocket

Las URLs WebSocket no deben depender de nombres de host fijos como:

```text
pos.local
```

El frontend debe utilizar el host desde el cual fue cargado cuando corresponda.

En producción:

```text
/ws
```

es gestionado mediante Nginx.

Esto permite acceso tanto mediante:

```text
http://pos.local
```

como mediante la IP local del servidor.

---

## Actualización de estado tras operaciones HTTP

Cuando una operación HTTP modifica el estado de negocio y la misma pantalla necesita reflejar inmediatamente el cambio, no debe depender exclusivamente de que llegue un evento WebSocket.

Ejemplo:

```typescript
await apiFetch(...)
await loadOrder()
```

Los WebSockets mantienen sincronizados los demás clientes.

La respuesta HTTP permite mantener consistente el cliente que inició la operación.

---

## Operaciones paralelas

Cuando varias operaciones independientes deben ejecutarse simultáneamente puede utilizarse:

```typescript
Promise.all(...)
```

Ejemplo:

```typescript
await Promise.all(
  readyItems.map(item =>
    apiFetch(`/order-items/${item.id}/status`, {
      method: "PATCH",
      body: {
        status: "DELIVERED"
      }
    })
  )
)
```

Debe utilizarse únicamente cuando las operaciones sean realmente independientes.

Si una operación depende del resultado de otra, deben ejecutarse secuencialmente.

---

## Navegación

La navegación interna debe realizarse mediante React Router.

Ejemplo:

```typescript
navigate(`/orders/${orderId}`)
```

No se utiliza:

```typescript
window.location.href = ...
```

para navegación normal dentro de la aplicación.

---

## Autenticación

El token de autenticación se envía mediante la utilidad común de API.

Los Components no deben construir manualmente el header:

```text
Authorization
```

en cada llamada.

La expiración o rechazo de autenticación debe gestionarse de forma centralizada.

---

## Roles y permisos

La interfaz puede ocultar o deshabilitar acciones según el rol del usuario.

Ejemplo:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

Pero:

> El frontend nunca se considera frontera de seguridad.

Los permisos deben validarse siempre en el backend.

Ocultar un botón es una decisión de experiencia de usuario, no una garantía de autorización.

---

## CSS

Se utiliza CSS para presentación visual.

Los nombres de clases deben ser descriptivos y relacionados con el componente o funcionalidad.

Ejemplo:

```css
.login-page
.login-card
.login-logo
.order-item
.cash-register-summary
```

Debe evitarse el uso excesivo de estilos inline.

Incorrecto:

```tsx
<img
  src={logo}
  width="300px"
  height="187px"
/>
```

Preferible:

```tsx
<img
  src={logo}
  className="login-logo"
/>
```

con:

```css
.login-logo {
  width: min(100%, 360px);
  height: auto;
}
```

Los estilos inline pueden utilizarse cuando el valor sea realmente dinámico.

---

## Responsive Design

La interfaz debe funcionar adecuadamente en:

- computadoras;
- tablets;
- teléfonos móviles.

Se debe prestar especial atención a las pantallas operativas:

- mesas;
- mozos;
- cocina;
- caja.

Los elementos interactivos deben mantener un tamaño apropiado para interfaces táctiles.

Debe evitarse diseñar exclusivamente para resolución de escritorio.

---

## Assets

Los recursos utilizados directamente por la aplicación deben organizarse dentro de:

```text
src/assets/
```

Ejemplo:

```text
src/
└── assets/
    ├── images/
    │   └── logo_marcha.jpeg
    └── sounds/
        └── bell.mp3
```

Se importan mediante Vite:

```typescript
import logoMarcha from "../assets/images/logo_marcha.jpeg"
import bellSound from "../assets/sounds/bell.mp3"
```

Los archivos de `public/` deben reservarse para recursos que necesiten conservar una URL o nombre fijo.

Ejemplos posibles:

- favicon;
- manifest;
- archivos públicos no importados por módulos TypeScript.

---

## Sonidos

Los sonidos deben importarse como assets.

Ejemplo:

```typescript
import bellSound from "../assets/sounds/bell.mp3"

const bell = new Audio(bellSound)
```

La reproducción debe manejar errores del navegador sin bloquear la aplicación.

Ejemplo:

```typescript
const playSound = () => {
  bell.currentTime = 0
  bell.play().catch(() => {})
}
```

---

## Nombres de archivos

Los nombres deben ser consistentes.

### Components

```text
ProductCard.tsx
DateRange.tsx
ProtectedRoute.tsx
```

### Pages

```text
LoginPage.tsx
TablesPage.tsx
KitchenPage.tsx
```

### Utilities

```text
apiFetch.ts
handleApiError.ts
showToast.ts
```

### Types

```text
orderStatus.ts
paymentMethod.ts
webSocketEvents.ts
```

Se debe respetar exactamente el casing utilizado en el nombre físico del archivo.

---

## Imports

Los imports deben mantenerse agrupados de forma legible.

Orden recomendado:

```text
React / librerías externas

API / hooks / context

components

types

utils

assets
```

Ejemplo:

```typescript
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { apiFetch } from "../api/apiFetch"

import ProductCard from "../components/ProductCard"

import type { Product } from "../types/product"

import { handleApiError } from "../utils/handleApiError"

import logoMarcha from "../assets/images/logo_marcha.jpeg"
```

No es necesario introducir una herramienta automática únicamente para imponer este orden si el código continúa siendo claro.

---

## Tipos importados

Cuando un import se utiliza únicamente como tipo, se prefiere:

```typescript
import type { Product } from "../types/product"
```

Esto hace explícita su finalidad.

---

## Funciones

Las funciones deben tener nombres que indiquen claramente su intención.

Preferible:

```typescript
loadProducts()
saveStation()
closeCashRegister()
playSound()
```

Evitar nombres genéricos como:

```typescript
doStuff()
handleData()
process()
```

cuando pueda expresarse una intención más precisa.

---

## Handlers

Los handlers asociados directamente a eventos de interfaz pueden utilizar nombres como:

```text
handleSubmit
handleDelete
handleStatusChange
handleDragEnd
```

Las funciones que ejecutan operaciones de dominio deberían utilizar nombres que describan la acción:

```text
saveProduct
loadOrder
closeOrder
deliverItems
```

---

## Async / Await

Se utiliza preferentemente `async/await`.

Ejemplo:

```typescript
const loadProducts = async () => {
  const data = await apiFetch("/products/")
  setProducts(data)
}
```

Debe evitarse mezclar innecesariamente:

```text
async/await
```

con:

```text
.then()
.catch()
```

dentro de la misma operación.

---

## Manejo de errores asíncronos

Las operaciones iniciadas desde acciones del usuario deben gestionar sus errores.

Ejemplo:

```typescript
const saveProduct = async () => {
  try {
    await apiFetch(...)
  } catch (error) {
    handleApiError(error)
  }
}
```

Cuando una función común ya se encargue completamente del tratamiento del error, no debe duplicarse el manejo.

---

## Loading y finally

Cuando una operación modifica un estado de carga, debe restaurarlo mediante `finally`.

Ejemplo:

```typescript
setLoading(true)

try {
  const data = await apiFetch(...)
  setProducts(data)
} catch (error) {
  handleApiError(error)
} finally {
  setLoading(false)
}
```

Esto evita dejar una pantalla permanentemente bloqueada después de un error.

---

## Valores derivados

Los valores que pueden calcularse a partir del estado existente no deben almacenarse como estado adicional salvo que exista una razón concreta.

Preferible:

```typescript
const remaining = total - paid
```

frente a:

```typescript
const [remaining, setRemaining] = useState(0)
```

si `remaining` puede derivarse siempre de otros valores.

Esto reduce estados inconsistentes.

---

## Estados del dominio

Los estados utilizados por el frontend deben corresponder a los definidos por el backend.

Ejemplo:

```text
OPEN
SENT
IN_PROGRESS
READY
CLOSED
CANCELLED
```

No deben inventarse estados equivalentes únicamente para presentación.

Si la interfaz necesita representar un concepto puramente visual, debe mantenerse claramente separado del estado de dominio.

---

## Dinero

Los valores monetarios recibidos desde la API deben tratarse de forma consistente.

La presentación debe realizarse mediante una utilidad común, por ejemplo:

```typescript
money.format(value)
```

No deben repetirse manualmente formatos monetarios en distintas Pages.

La lógica monetaria crítica permanece en el backend.

---

## IDs

Los IDs provenientes del backend no deben reinterpretarse como índices de arrays.

Correcto:

```typescript
products.find(product => product.id === productId)
```

Incorrecto conceptualmente:

```typescript
products[productId]
```

salvo que la estructura haya sido creada expresamente como mapa indexado por ID.

---

## Keys de React

Las listas deben utilizar identificadores estables.

Correcto:

```tsx
{products.map(product => (
  <ProductCard
    key={product.id}
    product={product}
  />
))}
```

Debe evitarse utilizar el índice del array como `key` cuando los elementos puedan cambiar de posición, agregarse o eliminarse.

---

## Accesibilidad básica

Los controles deben utilizar elementos HTML adecuados.

Ejemplo:

```text
button
input
label
select
```

en lugar de simular controles interactivos mediante `div`.

Las imágenes significativas deben utilizar `alt`.

Ejemplo:

```tsx
<img
  src={logoMarcha}
  alt="Marcha - Un aliado en tu Restaurant"
  className="login-logo"
/>
```

---

## Confirmaciones

Las operaciones potencialmente destructivas deben requerir confirmación cuando corresponda.

Ejemplos:

- eliminar registros;
- cancelar pedidos;
- restaurar backups;
- cerrar caja;
- acciones administrativas irreversibles.

La confirmación debe indicar claramente qué operación se realizará.

---

## Código duplicado

Cuando una misma lógica aparece repetida en varias Pages o Components debe evaluarse extraerla a:

```text
component
hook
utility
API helper
```

según su naturaleza.

No debe crearse una abstracción compartida únicamente porque dos bloques se parezcan superficialmente.

> Primero debe existir duplicación real. Después se abstrae.

---

## Comentarios

Los comentarios deben explicar decisiones o razones no evidentes.

Evitar comentarios que simplemente repitan el código.

Poco útil:

```typescript
// establecer loading a true
setLoading(true)
```

Útil:

```typescript
// Evitamos refrescar las mesas mientras se está arrastrando una,
// porque una actualización remota devolvería la mesa a su posición anterior.
if (draggingRef.current) return
```

---

## Console

No deben quedar `console.log()` de depuración en código de producción.

Pueden utilizarse temporalmente durante desarrollo.

Los errores inesperados pueden registrarse con:

```typescript
console.error(...)
```

cuando ayuden al diagnóstico, siempre que no expongan datos sensibles.

---

## Seguridad

El frontend nunca debe contener:

- contraseñas;
- claves privadas;
- secretos de API;
- `SECRET_KEY`;
- `ENCRYPTION_KEY`;
- credenciales de base de datos;
- información sensible de licenciamiento.

Las variables incluidas mediante Vite pueden terminar visibles en el navegador.

> Ningún valor secreto debe depender de permanecer oculto dentro del bundle frontend.

---

## Variables de entorno

Las variables frontend deben utilizarse únicamente para configuración que pueda ser pública.

Ejemplo:

```text
VITE_...
```

No deben almacenarse secretos en variables `VITE_*`.

En producción debe preferirse la detección del host actual o rutas relativas cuando evite configuración innecesaria.

---

## Build de producción

Antes de integrar cambios importantes al frontend debe ejecutarse:

```bash
npm run build
```

No basta con comprobar que funciona mediante:

```bash
npm run dev
```

El build de producción permite detectar problemas que pueden quedar ocultos en Windows o durante desarrollo.

Ejemplos ya relevantes para el proyecto:

- diferencias de mayúsculas/minúsculas en nombres de archivo;
- imports inexistentes;
- tipos duplicados;
- errores TypeScript;
- exports incompletos.

> Una modificación frontend no se considera lista únicamente porque funcione en Vite Development Server.

---

## Dependencias

No debe incorporarse una nueva librería para resolver un problema trivial que pueda solucionarse razonablemente con herramientas ya existentes.

Antes de agregar una dependencia debe evaluarse:

- necesidad real;
- mantenimiento;
- tamaño;
- compatibilidad;
- frecuencia de actualización;
- impacto en el bundle.

Las dependencias no utilizadas deben eliminarse.

---

## Compatibilidad

La aplicación debe mantenerse funcional en navegadores modernos utilizados por los dispositivos objetivo.

Debe prestarse especial atención a:

- Chrome/Chromium en Android;
- navegadores modernos de escritorio;
- soporte de WebSockets;
- reproducción de audio;
- interfaces táctiles.

---

## Filosofía

> La interfaz debe ser rápida de entender durante un turno de trabajo.

Marcha no es una aplicación donde el usuario deba detenerse a interpretar la interfaz.

Se prioriza:

- claridad;
- velocidad operativa;
- pocas acciones por tarea;
- feedback inmediato;
- botones comprensibles;
- estados visuales claros;
- comportamiento consistente.

Una solución visual más sofisticada no es necesariamente mejor si requiere más tiempo o atención del usuario.

---

## Regla final

Cuando se agrega una nueva funcionalidad frontend debería ser posible identificar claramente:

```text
Page / Component
      ↓
apiFetch
      ↓
Backend API
      ↓
actualización de estado
      ↓
feedback visual
```

Y, cuando existe sincronización en tiempo real:

```text
Backend
   ↓
WebSocket event
   ↓
Frontend
   ↓
refresco o actualización del estado
```

Si una Page empieza a concentrar:

- lógica HTTP repetida;
- reglas de negocio;
- parsing de errores;
- estilos inline extensos;
- código reutilizable;
- múltiples responsabilidades no relacionadas;

probablemente sea momento de separar responsabilidades.