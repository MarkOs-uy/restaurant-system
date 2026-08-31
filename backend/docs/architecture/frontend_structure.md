# Frontend Structure

## Objetivo

El frontend de Marcha está organizado para separar claramente:

- navegación;
- páginas;
- componentes visuales;
- acceso a API;
- tipos;
- utilidades;
- assets;
- comunicación en tiempo real.

El objetivo principal es mantener una interfaz:

- simple de comprender;
- rápida de modificar;
- consistente;
- reutilizable;
- tipada;
- desacoplada de las reglas de negocio.

La regla principal es:

> El frontend presenta el estado del sistema y captura acciones del usuario.  
> El backend conserva la autoridad sobre las reglas de negocio.

---

## Estructura general

La estructura principal del frontend sigue este esquema:

```text
src/
├── api/
├── assets/
│   ├── images/
│   └── sounds/
├── components/
├── context/
├── hooks/
├── pages/
├── types/
├── utils/
├── App.tsx
└── main.tsx
```

La estructura puede evolucionar, pero las responsabilidades de cada carpeta deben mantenerse claras.

No se deben crear carpetas únicamente por seguir una convención si no existe una responsabilidad real que las justifique.

---

## Flujo general de una operación

Una operación habitual del usuario sigue este recorrido:

```text
Usuario
   ↓
Page / Component
   ↓
apiFetch
   ↓
Nginx
   ↓
Backend API
   ↓
respuesta
   ↓
actualización de estado
   ↓
render
```

Cuando intervienen eventos en tiempo real:

```text
Backend
   ↓
Redis / WebSocket
   ↓
Frontend
   ↓
actualización o recarga del recurso
   ↓
render
```

---

## Pages

La carpeta `pages/` contiene las vistas principales de la aplicación.

Normalmente una Page corresponde a:

- una ruta;
- una pantalla operativa;
- un módulo funcional completo.

Ejemplos:

```text
LoginPage
TablesPage
OrderDetailPage
KitchenPage
CashierPage
ProductsPage
StationsPage
BackupsPage
ReportsPage
```

Las Pages pueden:

- cargar información;
- mantener estado local;
- reaccionar a WebSockets;
- navegar entre rutas;
- coordinar Components;
- ejecutar llamadas mediante `apiFetch`;
- gestionar loading y errores.

Las Pages no deberían concentrar toda la lógica visual de una funcionalidad compleja cuando existen bloques claramente separables.

---

## Components

La carpeta `components/` contiene elementos reutilizables o unidades visuales independientes.

Ejemplos:

```text
ProtectedRoute
DateRange
ProductCard
OrderItemRow
StatusBadge
Modal
ConfirmDialog
```

Un Component debe tener una responsabilidad clara.

Debe evaluarse extraer un bloque a Component cuando:

- se utiliza en más de una pantalla;
- posee lógica visual propia;
- tiene estado independiente;
- facilita significativamente la lectura de una Page.

No debe extraerse código únicamente para reducir el número de líneas de un archivo.

> La reutilización y la claridad justifican un Component; la cantidad de líneas por sí sola no.

---

## API

La carpeta `api/` concentra la comunicación HTTP con el backend.

Ejemplo:

```text
api/
├── apiFetch.ts
└── ...
```

Las Pages y Components no deberían utilizar `fetch()` directamente cuando existe una abstracción común.

El acceso habitual debe realizarse mediante:

```typescript
apiFetch(...)
```

Esto permite centralizar:

- autenticación;
- headers;
- manejo JSON;
- errores;
- respuestas `401`;
- configuración común.

Ejemplo:

```typescript
const products = await apiFetch("/products/")
```

---

## Comunicación HTTP

En producción, el frontend no se comunica directamente con un host o puerto fijo del backend.

El flujo es:

```text
Browser
   ↓
/api/...
   ↓
Nginx
   ↓
FastAPI
```

Esto permite acceder a Marcha mediante:

```text
http://pos.local
```

o:

```text
http://<IP-servidor>
```

sin recompilar el frontend para cada instalación.

---

## Types

La carpeta `types/` contiene tipos TypeScript compartidos.

Ejemplo:

```text
types/
├── order.ts
├── orderStatus.ts
├── paymentMethod.ts
├── product.ts
├── userRole.ts
├── webSocketEvents.ts
└── index.ts
```

Los tipos utilizados únicamente dentro de una Page o Component pueden permanecer definidos junto a ese módulo.

Los tipos compartidos entre varias áreas deben trasladarse a `types/`.

---

## Barrel de tipos

Puede utilizarse:

```text
types/index.ts
```

para centralizar exports compartidos.

Ejemplo:

```typescript
export * from "./order"
export * from "./orderStatus"
export * from "./paymentMethod"
export * from "./webSocketEvents"
```

No deben existir nombres duplicados exportados por distintos módulos.

El casing de archivos e imports debe coincidir exactamente.

Ejemplo:

```text
webSocketEvents.ts
```

debe importarse como:

```typescript
import type { WebSocketEvent } from "../types/webSocketEvents"
```

y no mediante una variante de mayúsculas/minúsculas.

Esto es especialmente importante porque Linux es case-sensitive.

---

## Utils

La carpeta `utils/` contiene funciones genéricas reutilizables que no pertenecen específicamente a una Page o Component.

Ejemplos:

```text
utils/
├── handleApiError.ts
├── showToast.ts
├── money.ts
└── ...
```

Una Utility debe ser:

- reutilizable;
- independiente de una pantalla específica;
- pequeña;
- fácil de testear.

No debe utilizarse `utils/` como carpeta genérica para código cuya responsabilidad no esté clara.

---

## Manejo de errores

Los errores de API deben procesarse de forma centralizada.

Flujo habitual:

```text
Backend
   ↓
DomainError / ErrorCode
   ↓
HTTP response
   ↓
apiFetch
   ↓
handleApiError
   ↓
mensaje de usuario
```

Las Pages no deberían duplicar la interpretación de errores.

Ejemplo:

```typescript
try {
  await apiFetch(...)
} catch (error) {
  handleApiError(error)
}
```

---

## Toasts

Las notificaciones no bloqueantes se muestran mediante el sistema común de toast.

Ejemplo:

```typescript
showToast("Producto guardado")
```

Los mensajes deben ser:

- breves;
- claros;
- comprensibles;
- sin información técnica innecesaria.

Se evita utilizar `alert()` como mecanismo habitual de interfaz.

---

## Context

La carpeta `context/` puede utilizarse para estado realmente transversal.

Ejemplos posibles:

```text
Authentication
CurrentUser
Global configuration
```

No debe trasladarse estado a Context únicamente para evitar pasar una o dos props.

El estado local debe seguir siendo la opción preferida cuando pertenece a una sola Page o grupo reducido de Components.

---

## Hooks

La carpeta `hooks/` puede contener lógica reutilizable basada en hooks de React.

Ejemplos posibles:

```text
useAuth
useWebSocket
useCurrentUser
```

Un custom hook debe extraerse cuando exista:

- lógica reutilizada;
- coordinación repetida de efectos;
- una responsabilidad claramente independiente.

No se deben crear hooks triviales que únicamente oculten pocas líneas sin aportar una abstracción útil.

---

## WebSockets

Marcha utiliza WebSockets para mantener sincronizados los distintos puestos de trabajo.

Ejemplos de eventos:

```text
ORDER_UPDATED
ORDER_STATUS_CHANGED
ITEM_STATUS_CHANGED
ITEM_READY
PAYMENT_ADDED
CASH_REGISTER_UPDATED
```

Las Pages deben reaccionar únicamente a los eventos que afectan su información.

La filosofía general es:

> WebSocket notifica que algo cambió.  
> HTTP proporciona el estado actual definitivo.

Por ello, cuando corresponda, un evento puede disparar una nueva consulta HTTP en lugar de reconstruir todo el estado local desde el payload recibido.

---

## Conexión WebSocket

La conexión WebSocket no debe depender de una dirección fija como:

```text
ws://pos.local:8000
```

En producción, la conexión utiliza el mismo host desde el cual se cargó la aplicación y pasa por Nginx.

Flujo:

```text
Browser
   ↓
/ws
   ↓
Nginx
   ↓
FastAPI WebSocket
```

Esto permite utilizar Marcha mediante nombre mDNS o IP local.

---

## Estado local

Se utiliza `useState` para estado propio de una pantalla o componente.

Ejemplo:

```typescript
const [products, setProducts] = useState<Product[]>([])
```

Debe evitarse almacenar valores que pueden derivarse directamente de otro estado.

Preferible:

```typescript
const remaining = total - paid
```

en lugar de:

```typescript
const [remaining, setRemaining] = useState(0)
```

cuando el valor pueda calcularse siempre.

---

## useEffect

`useEffect` se utiliza para sincronización con sistemas externos.

Casos habituales:

- carga inicial;
- WebSockets;
- timers;
- event listeners;
- subscriptions.

Ejemplo:

```typescript
useEffect(() => {
  loadProducts()
}, [])
```

Los efectos que creen recursos deben limpiarlos.

Ejemplo:

```typescript
useEffect(() => {
  const socket = new WebSocket(url)

  return () => {
    socket.close()
  }
}, [])
```

---

## Estado después de una operación HTTP

Cuando una acción HTTP modifica el recurso que la pantalla está mostrando, el cliente que inició la operación debe actualizar su estado directamente.

Ejemplo:

```typescript
await apiFetch(...)
await loadOrder()
```

No debe depender exclusivamente de recibir su propio evento WebSocket.

El evento sirve principalmente para sincronizar otros clientes conectados.

---

## Assets

Los recursos utilizados por la aplicación se almacenan en:

```text
src/assets/
```

Ejemplo:

```text
assets/
├── images/
│   └── logo_marcha.jpeg
└── sounds/
    └── bell.mp3
```

Se importan desde TypeScript:

```typescript
import logoMarcha from "../assets/images/logo_marcha.jpeg"
import bellSound from "../assets/sounds/bell.mp3"
```

Vite procesa estos archivos durante el build y puede generar nombres versionados.

---

## Public

La carpeta `public/` se reserva para archivos que deban conservar una ruta o nombre fijo.

Ejemplos:

```text
favicon
manifest
robots.txt
```

Los recursos que forman parte directamente de la interfaz deberían preferentemente encontrarse en `src/assets/`.

---

## CSS

Los estilos deben asociarse mediante clases descriptivas.

Ejemplo:

```css
.login-page
.login-card
.login-logo
.order-item
.cash-register-summary
```

Debe evitarse el uso extensivo de estilos inline.

Los estilos inline pueden utilizarse cuando el valor depende realmente del estado o de información dinámica.

---

## Responsive Design

Marcha está pensado para funcionar en:

- computadoras;
- tablets;
- teléfonos.

Las pantallas operativas requieren especial atención a dispositivos táctiles.

Ejemplos:

```text
Tables
Waiter
Kitchen
Cashier
```

La interfaz debe evitar depender exclusivamente de:

- hover;
- pantallas grandes;
- mouse;
- resoluciones de escritorio.

---

## Navegación

La navegación interna se realiza mediante React Router.

Ejemplo:

```typescript
navigate(`/orders/${orderId}`)
```

No debe utilizarse `window.location.href` para navegación habitual dentro de la SPA.

---

## App.tsx

`App.tsx` define principalmente:

- rutas;
- protección de rutas;
- composición general de la aplicación.

No debe convertirse en un lugar para almacenar lógica de negocio o lógica específica de Pages.

Ejemplo conceptual:

```text
App
├── /login
├── /tables
├── /orders/:id
├── /kitchen
├── /cashier
├── /products
└── ...
```

---

## main.tsx

`main.tsx` constituye el punto de entrada del frontend.

Debe limitarse principalmente a:

- inicializar React;
- montar la aplicación;
- registrar providers globales;
- cargar estilos globales.

No debe contener lógica funcional de negocio.

---

## Roles

La interfaz adapta sus opciones según el rol autenticado.

Roles actuales:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

La interfaz puede:

- ocultar acciones;
- deshabilitar botones;
- mostrar vistas específicas.

Estas restricciones mejoran la experiencia del usuario.

No constituyen una frontera de seguridad.

> El backend siempre valida nuevamente los permisos.

---

## Estados del dominio

El frontend utiliza los estados definidos por el backend.

Ejemplo:

```text
OPEN
SENT
IN_PROGRESS
READY
CLOSED
CANCELLED
```

No deben crearse estados alternativos que representen lo mismo con nombres distintos.

Los estados puramente visuales deben mantenerse separados de los estados de dominio.

---

## Build de producción

El frontend de producción se construye mediante Vite.

Flujo:

```text
src/
   ↓
npm run build
   ↓
dist/
   ↓
Docker build
   ↓
Nginx
```

Los cambios realizados en `src/` no afectan automáticamente a una instalación productiva existente.

Es necesario reconstruir la imagen frontend.

---

## Diferencias desarrollo / producción

### Desarrollo

```text
Vite Development Server
   ↓
Hot Reload
```

Los cambios aparecen inmediatamente.

### Producción

```text
Source
   ↓
Vite build
   ↓
Docker image
   ↓
Nginx
```

Por lo tanto:

> `git pull` actualiza el código fuente, pero no modifica por sí solo el frontend que está sirviendo un contenedor ya construido.

El proceso normal de `update.sh` se encarga del nuevo build.

---

## Dependencias permitidas

Relaciones habituales:

```text
Page
  ↓
Component

Page
  ↓
apiFetch

Page / Component
  ↓
types

Page / Component
  ↓
utils

Page / Component
  ↓
assets

Hook
  ↓
api / utils
```

Debe evitarse introducir dependencias circulares entre Components o Pages.

También debe evitarse:

```text
api
 ↓
Page

types
 ↓
Page

utils
 ↓
Page específica
```

Las capas reutilizables no deben depender de la interfaz que las consume.

---

## Principios generales

Una Page responde a:

> ¿Qué necesita mostrar y coordinar esta pantalla?

Un Component responde a:

> ¿Qué unidad visual representa?

`api/` responde a:

> ¿Cómo se comunica el frontend con el backend?

`types/` responde a:

> ¿Qué estructuras TypeScript compartimos?

`utils/` responde a:

> ¿Qué comportamiento genérico reutilizamos?

`assets/` responde a:

> ¿Qué recursos visuales o sonoros forman parte de la aplicación?

---

## Regla final

Cuando se implementa una nueva funcionalidad debería ser posible identificar claramente:

```text
Page
   ↓
Components
   ↓
apiFetch
   ↓
Backend
```

y, si existe tiempo real:

```text
Backend
   ↓
WebSocket
   ↓
Page
   ↓
refresco / actualización
```

Si una Page empieza a contener:

- lógica HTTP duplicada;
- interpretación repetida de errores;
- reglas de negocio;
- grandes bloques visuales reutilizables;
- estilos extensos inline;
- múltiples responsabilidades independientes;

probablemente sea necesario separar responsabilidades.