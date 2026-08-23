# ADR 0004: El identificador es un UUIDv4 que genera la entidad

**Estado:** aceptada
**Fecha:** 2026-08-22

## Contexto

Un producto necesita identidad. La opción por defecto en Django es un `AutoField` entero que asigna la base de datos al insertar. Eso tiene una consecuencia incómoda para el diseño del [ADR 0003](0003-entidad-de-dominio-pura.md): la entidad existe sin identidad hasta que alguien la persiste, y el dominio pasa a depender de la base para algo tan básico como saber quién es un objeto.

## Alternativas consideradas

| Opción | A favor | En contra |
|---|---|---|
| `AutoField` entero autoincremental | Índice compacto, es el default de Django | La identidad la asigna la DB; la entidad queda a medias hasta el insert. Expone el volumen de datos y es enumerable desde afuera |
| `UUIDField` con `default=uuid4` en el modelo | Sigue siendo un UUID y no hay que hacer nada | Quien genera el id es la capa de infraestructura, no el dominio |
| UUIDv4 generado por la entidad | La entidad nace completa; el id no depende de la DB ni del ORM | Índice de 16 bytes y escritura no secuencial, con más fragmentación en InnoDB |
| UUIDv7 | Ordenable por tiempo, mejor localidad en el índice | Soporte todavía irregular en el ecosistema; `uuid7` no está en la stdlib de la versión en uso |

## Decisión

`Product.id` es un `UUID` con `default_factory=uuid4`, generado en el dominio.

El `UUIDField` del modelo va **sin `default`**: la infraestructura no inventa ids, solo persiste el que le llega. Esto tiene un efecto directo en el repositorio: como el id ya viene puesto, Django no puede distinguir un insert de un update, así que `create` usa `.save(force_insert=True)` para forzar el INSERT.

## Consecuencias

- Una entidad recién construida ya tiene identidad, antes de tocar la base. Se puede comparar, loguear y devolver sin haber persistido nada.
- Los ids no son enumerables desde afuera: no se puede recorrer `/products/1/`, `/products/2/` y sacar el catálogo entero.
- El índice primario pasa de 4 a 16 bytes y las inserciones no son secuenciales. Con el volumen de este proyecto no importa; en una tabla de millones de filas habría que revisarlo.
- Las rutas usan el converter `<uuid:product_id>`, así que un id con formato inválido lo rechaza Django con 404 antes de llegar a la vista. El caso de uso solo ve UUIDs bien formados.
- Cambiar de `uuid4` a `uuid7` más adelante es tocar una línea de la entidad; nada afuera del dominio asume cómo se genera.
