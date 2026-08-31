# MEMORIA DESCRIPTIVA: MARCHA

## Sistema de gestión integral para restaurantes
> Autor / Titular: Marcos Mato Toledo

> Nombre del software: Marcha

> Tipo de obra: Software de aplicación / Sistema de gestión gastronómica

> Versión: 1.0

> Año de desarrollo: 2026

> Estado: Versión funcional en etapa de validación comercial

## 1. Descripción general

Marcha es un sistema informático de gestión integral destinado a restaurantes y establecimientos gastronómicos.

El software fue diseñado para administrar de forma coordinada las principales operaciones que ocurren durante el servicio de un restaurante, incluyendo la gestión de mesas, toma de pedidos, producción en cocina o estaciones de trabajo, entrega de productos, cobros, caja, administración de productos, usuarios, reportes y respaldos de información.

Una de sus características principales es que está concebido bajo un modelo de operación local y autónomo, permitiendo que el establecimiento continúe funcionando aun cuando no disponga de conexión a Internet.

Marcha utiliza un servidor instalado dentro del propio establecimiento y distintos dispositivos conectados a la red local, tales como computadoras, tablets o teléfonos móviles.

El sistema fue desarrollado específicamente buscando simplicidad operativa, rapidez de uso y adaptación al flujo de trabajo cotidiano de restaurantes.

## 2. Objetivo del sistema
El objetivo principal de Marcha es centralizar y sincronizar las distintas etapas de funcionamiento de un restaurante.
El sistema procura reducir problemas habituales de la operativa gastronómica, tales como:
- errores en la transmisión de pedidos; 
- pérdida o duplicación de comandas; 
- falta de sincronización entre salón, cocina y caja; 
- dificultad para conocer el estado de cada pedido; 
- demoras en la comunicación entre áreas; 
- falta de control sobre los movimientos de caja; 
- dependencia de registros manuales; 
- dificultad para obtener información histórica de ventas; 
- dependencia de servicios externos o conexión permanente a Internet.

Marcha proporciona una única plataforma desde la cual los distintos perfiles de usuario acceden únicamente a las funciones necesarias para su trabajo.

## 3. Usuarios del sistema
El sistema contempla diferentes perfiles o roles operativos.

> Administrador

Permite configurar y administrar el establecimiento.
Entre sus funciones se encuentran:
- administración de usuarios; 
- administración de productos; 
- administración de categorías; 
- configuración de estaciones de producción; 
- configuración de mesas; 
- configuración del plano del restaurante; 
- consulta de reportes; 
- administración de respaldos; 
- configuración general del sistema. 

> Mozo

Permite gestionar la atención de las mesas.
Entre sus funciones se encuentran:
- visualizar mesas; 
- abrir pedidos; 
- agregar productos; 
- modificar cantidades mientras el pedido lo permita; 
- agregar observaciones; 
- enviar productos a producción; 
- consultar el estado de los pedidos; 
- identificar productos preparados; 
- registrar la entrega de productos;
- aplicar descuentos a las ordenes;
- cobrar las ordenes;
- cerrar las ordenes.

> Cocina / Producción

Permite visualizar y gestionar los productos enviados a las distintas estaciones de producción.
Cada estación puede recibir únicamente los productos que le corresponden.

Los productos evolucionan mediante diferentes estados que representan su situación dentro del proceso de preparación.

> Caja

Permite gestionar operaciones económicas asociadas al servicio.
Incluye:
- apertura de caja; 
- registro de pagos; 
- utilización de diferentes medios de pago; 
- movimientos de ingreso y egreso de efectivo; 
- consulta del estado de caja; 
- cierre de caja; 
- control de diferencias entre efectivo esperado y efectivo contabilizado. 

## 4. Gestión de mesas
Marcha permite representar las mesas del establecimiento mediante una interfaz gráfica.
Cada mesa puede almacenar información relacionada con:
- número; 
- ubicación; 
- forma; 
- capacidad; 
- orientación; 
- estado; 
- pedido activo. 

El administrador puede configurar la distribución de las mesas para aproximarla a la disposición física del establecimiento.

El estado visual de cada mesa permite identificar rápidamente si se encuentra libre o asociada a un pedido activo.

## 5. Gestión de pedidos
Los pedidos constituyen una de las entidades centrales del sistema.

Cada pedido se encuentra asociado a un restaurante y, cuando corresponde, a una mesa.

Un pedido contiene uno o más productos denominados internamente ítems de pedido.

El sistema controla el ciclo de vida del pedido y evita transiciones incompatibles con las reglas de negocio.

Entre las operaciones disponibles se encuentran:
- creación de pedidos; 
- incorporación de productos; 
- modificación de cantidades; 
- incorporación de observaciones; 
- envío a producción; 
- seguimiento del estado de preparación; 
- entrega; 
- cancelación; 
- aplicación de descuentos; 
- registro de pagos; 
- cierre. 

El sistema verifica las condiciones necesarias antes de permitir determinadas operaciones.
Por ejemplo, un pedido no puede cerrarse mientras existan importes pendientes o productos cuya situación no permita el cierre.

## 6. Gestión de productos solicitados
Cada producto agregado a un pedido posee su propio estado.

Esto permite conocer individualmente si un producto:
- todavía no fue enviado; 
- fue enviado a producción; 
- se encuentra en preparación; 
- está preparado; 
- fue entregado; 
- fue cancelado. 

Esta administración independiente permite trabajar correctamente con pedidos que contienen productos preparados en distintos tiempos o estaciones.

Los productos aún no enviados pueden eliminarse cuando corresponde.

Una vez incorporados al proceso operativo, las cancelaciones conservan la información histórica necesaria para mantener la trazabilidad de la operación.

## 7. Estaciones de producción
Los productos pueden asociarse a distintas estaciones de producción.

Ejemplos posibles:
- cocina; 
- barra; 
- parrilla; 
- cafetería; 
- postres. 

Cada estación recibe únicamente los productos que tiene asignados.
Esto permite que un mismo pedido sea distribuido automáticamente entre diferentes sectores del establecimiento.
Las estaciones pueden activarse o desactivarse sin necesidad de eliminar su información histórica.

## 8. Comunicación en tiempo real
Marcha incorpora mecanismos de comunicación en tiempo real para mantener sincronizadas las distintas terminales.

Cuando ocurre una operación relevante, el sistema puede informar inmediatamente a los clientes conectados.

Por ejemplo:
- envío de un pedido a cocina; 
- inicio de preparación; 
- producto preparado; 
- producto entregado; 
- actualización de pedido; 
- registro de un pago; 
- modificación del estado de caja. 

Esto permite que los distintos sectores trabajen sobre información actualizada sin necesidad de realizar recargas manuales permanentes.

## 9. Gestión de pagos
Marcha permite registrar uno o varios pagos asociados a un pedido.

El sistema contempla diferentes métodos de pago, entre ellos:
- efectivo; 
- tarjeta; 
- transferencia.

El sistema calcula:
- subtotal; 
- descuentos; 
- total; 
- importe abonado; 
- saldo pendiente. 

Se incluyen validaciones para evitar operaciones inconsistentes, como registrar determinados pagos por importes incompatibles con el saldo existente.

## 10. Gestión de caja
El sistema posee un módulo específico de caja.
La caja puede abrirse indicando un importe inicial.

Durante la operación se registran:
- ventas; 
- cobros; 
- ingresos de efectivo; 
- egresos de efectivo. 

Al finalizar la jornada puede realizarse un cierre indicando el efectivo contado.
Marcha calcula el efectivo esperado y compara dicho valor con el importe registrado por el usuario.

El sistema conserva información del cierre y de los medios de pago utilizados.

## 11. Administración de productos y categorías
Los productos utilizados por Marcha pueden organizarse mediante categorías.

Cada producto puede contener, entre otros datos:
- nombre; 
- precio; 
- categoría; 
- estación de producción; 
- estado activo o inactivo. 

La activación o desactivación permite conservar información histórica sin necesidad de eliminar registros utilizados previamente.

## 12. Administración de usuarios
Marcha posee autenticación de usuarios y control de acceso según roles.
Cada usuario pertenece a un restaurante y posee permisos asociados a su función.

Los roles actualmente contemplados son:
- administrador; 
- mozo; 
- cocina; 
- caja. 

El backend verifica los permisos correspondientes independientemente de las restricciones aplicadas por la interfaz de usuario.

## 13. Separación de datos por restaurante
El modelo de datos contempla la posibilidad de administrar información perteneciente a diferentes restaurantes.
Las principales entidades operativas se encuentran asociadas a un identificador de restaurante.
El backend verifica dicha pertenencia al realizar operaciones sobre los recursos.
De esta forma se mantiene una separación lógica entre los datos correspondientes a distintos establecimientos.

## 14. Reportes
Marcha incluye herramientas de consulta y análisis de la información generada durante la operación.

Según la información disponible, pueden obtenerse reportes relacionados con:
- ventas; 
- períodos de tiempo; 
- productos; 
- productos más vendidos; 
- productos menos vendidos; 
- evolución de ventas; 
- medios de pago; 
- operaciones de caja; 
- comportamiento histórico del establecimiento. 

Los reportes se obtienen a partir de la información almacenada por el propio sistema.

## 15. Sistema de respaldo
Marcha dispone de un sistema integrado de copias de seguridad.

El sistema permite realizar:
- backups manuales; 
- backups automáticos; 
- backups diarios; 
- backups semanales; 
- backups mensuales; 
- políticas de retención; 
- respaldos previos a procesos de restauración; 
- descarga de respaldos; 
- eliminación de respaldos; 
- restauración de información. 

Opcionalmente los respaldos pueden enviarse mediante correo electrónico cuando el establecimiento dispone de la configuración necesaria.
El funcionamiento principal del sistema no depende del servicio de correo electrónico.

## 16. Arquitectura técnica
Marcha utiliza una arquitectura cliente-servidor.

De forma simplificada:
```text
Tablets / teléfonos / computadoras
              ↓
         Red local
              ↓
            Nginx
        ↙            ↘
   Frontend        Backend
    React          FastAPI
                      ↓
                 PostgreSQL
                      ↕
                    Redis
```
Los dispositivos cliente acceden al sistema utilizando un navegador web.

El frontend se comunica con el backend mediante una API HTTP y mediante conexiones WebSocket para determinadas actualizaciones en tiempo real.

## 17. Tecnologías utilizadas
La aplicación utiliza principalmente las siguientes tecnologías.
> Backend
- Python; 
- FastAPI; 
- SQLAlchemy; 
- Pydantic; 
- Alembic. 
> Base de datos
- PostgreSQL. 
> Comunicación y eventos
- WebSockets; 
- Redis. 
> Frontend
- TypeScript; 
- React; 
- Vite. 
> Infraestructura
- Docker; 
- Docker Compose; 
- Nginx; 
- systemd; 
> Linux Debian/Ubuntu. 

## 18. Organización interna del backend
El backend se encuentra organizado por capas y módulos funcionales.

La estructura separa principalmente:
- capa HTTP; 
- lógica de dominio; 
- modelos de persistencia; 
- schemas de entrada y salida; 
- gestión de base de datos; 
- infraestructura; 
- eventos; 
- WebSockets; 
- tareas programadas. 

La lógica de negocio se concentra principalmente en Services.
Los Routers se utilizan como interfaz entre el protocolo HTTP y dicha lógica de negocio.
Esta separación permite mantener las reglas principales independientes de la interfaz utilizada por el usuario.

## 19. Persistencia y migraciones
Marcha utiliza PostgreSQL como sistema de persistencia principal.
La estructura de la base de datos se encuentra versionada mediante Alembic.
Las modificaciones del esquema se implementan mediante migraciones controladas, lo que permite reproducir la estructura de la base de datos y actualizar instalaciones existentes.

## 20. Instalación y ejecución
Marcha se distribuye para funcionar sobre un servidor Linux compatible.
El sistema incluye procedimientos automatizados para:
- instalación; 
- configuración; 
- construcción de contenedores; 
- inicio; 
- detención; 
- actualización; 
- desinstalación. 

`Docker Compose` administra los principales componentes de la aplicación.

`systemd` administra el ciclo de vida del sistema en el servidor.

El frontend se publica mediante Nginx y constituye el punto principal de acceso desde la red local.

## 21. Funcionamiento independiente de Internet
Una característica fundamental de Marcha es que las operaciones principales del restaurante no requieren acceso a Internet.

Una vez instalado, el establecimiento puede continuar utilizando:
- mesas; 
- pedidos; 
- cocina; 
- caja; 
- productos; 
- usuarios; 
- reportes y  
- backups locales utilizando únicamente su red local.

Determinadas funciones complementarias, como el envío de respaldos por correo electrónico, requieren conectividad externa.

## 22. Sistema de licencia
Marcha incorpora un mecanismo de licencia local destinado a controlar instalaciones autorizadas.
La licencia es verificada por el backend durante el proceso de inicio.
La validación puede realizarse sin conexión a Internet mediante técnicas criptográficas de firma digital.
La licencia se encuentra vinculada a características estables de la máquina en la cual fue autorizada.
El sistema distribuido contiene únicamente los componentes necesarios para verificar las licencias y no incluye los elementos privados utilizados para emitirlas.

## 23. Seguridad
Marcha incorpora diferentes mecanismos relacionados con seguridad e integridad del sistema.

Entre ellos:
- autenticación de usuarios; 
- autorización por roles; 
- aislamiento lógico por restaurante; 
- validación de reglas en el backend; 
- utilización de tokens de autenticación; 
- separación entre frontend y reglas de negocio; 
- cifrado de determinadas credenciales sensibles almacenadas; 
- licencia firmada digitalmente; 
- backups de información; 
- separación de secretos mediante configuración externa al código fuente. 

La seguridad del sistema no depende exclusivamente de validaciones realizadas por el frontend.

## 24. Características particulares del desarrollo
Marcha fue diseñado específicamente teniendo en cuenta las condiciones de operación de pequeños y medianos establecimientos gastronómicos.

Entre los criterios aplicados durante su desarrollo se encuentran:
- funcionamiento dentro de la red local; 
- mínima dependencia de Internet; 
- utilización desde dispositivos móviles comunes; 
- separación de funciones según el rol del trabajador; 
- sincronización en tiempo real; 
- conservación de información histórica; 
- control explícito de estados; 
- facilidad de instalación; 
- facilidad de actualización; 
- respaldo y recuperación de datos; 
- posibilidad de evolución futura del producto. 

## 25. Código fuente
El sistema ha sido desarrollado como una aplicación propia y se encuentra compuesto por código fuente correspondiente, entre otros elementos, a:
- backend; 
- frontend; 
- modelos; 
- schemas; 
- servicios; 
- lógica de dominio; 
- componentes visuales; 
- comunicación en tiempo real; 
- scripts de instalación; 
- scripts de actualización; 
- scripts de administración; 
- sistema de backups; 
- sistema de licenciamiento. 

El software utiliza además bibliotecas y componentes de terceros sujetos a sus respectivas licencias.
Dichos componentes constituyen dependencias tecnológicas y no sustituyen el código y lógica específica desarrollados para Marcha.

## 26. Estado actual del proyecto
A la fecha de esta memoria, Marcha dispone de una versión funcional capaz de realizar el ciclo operativo principal de un restaurante.

El sistema ha sido sometido a pruebas de:
- instalación desde un sistema limpio; 
- creación y actualización de base de datos; 
- autenticación; 
- gestión de pedidos; 
- comunicación en tiempo real; 
- caja; 
- backups; 
- actualización del software; 
- inicio y detención de servicios; 
- desinstalación; 
- reinstalación preservando datos; 
- validación de licencias. 

El producto se encuentra en etapa de validación mediante uso en condiciones reales de operación.

## 27. Evolución prevista
La arquitectura del sistema permite incorporar nuevas funcionalidades sin alterar los principios fundamentales de funcionamiento.
Posibles evoluciones del producto pueden incluir nuevas herramientas operativas, reportes, integraciones externas y funciones comerciales.
Estas futuras ampliaciones no modifican la naturaleza principal del software descripto en esta memoria.

## 28. Síntesis
Marcha es una plataforma integral de gestión gastronómica desarrollada para coordinar en tiempo real las principales operaciones de un restaurante.

Su diseño combina:
- gestión de salón; 
- gestión de pedidos; 
- producción; 
- caja; 
- administración; 
- reportes; 
- backups; 
- operación local; 
- sincronización en tiempo real; 
- mecanismos de seguridad y licenciamiento. 

El sistema está especialmente orientado a proporcionar una solución autónoma, mantenible y adaptable para establecimientos que requieren continuidad operativa independientemente de la disponibilidad de conexión a Internet.

> Autor: Marcos Mato Toledo

> Lugar y fecha: Barra de Valizas, Uruguay — 30/08/2026

> Versión del software documentada: Marcha 1.0
