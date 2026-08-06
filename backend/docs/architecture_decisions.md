Estaciones

- Los mozos no consultan estaciones.
- Cocina consulta estaciones activas.
- Las estaciones nunca se eliminan.
- Las estaciones sólo pueden activarse/desactivarse.
- El nombre de una estación nunca puede ser nulo.



GET: siempre devuelve recursos.
POST: devuelve el recurso creado.
PATCH: devuelve el recurso actualizado solo si el cliente lo utiliza; si el cliente siempre hace un GET después, puede responder 204 No Content.
DELETE: normalmente 204 No Content.